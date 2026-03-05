import logging
from django.db import transaction
from typing import List
from ..models import Table
from ..exceptions import *

logger = logging.getLogger(__name__)

class TableService:
    MAX_ALLOWED_CAPACITY = 20
    RESTAURANT_MAX_TABLES = 100

    @classmethod
    def _validate_common_table_fields(cls, capacity: int, number: int, instance_id: int = None):
        """
        Performs common validations for table creation and update.
        instance_id is used to exclude the current table when checking for unique number during update.
        """
        if capacity > cls.MAX_ALLOWED_CAPACITY:
            raise TableCapacityExceeded(f"Capacity out of range. Maximum capacity is {cls.MAX_ALLOWED_CAPACITY}.")

        query = Table.objects.filter(number=number)
        if instance_id:
            query = query.exclude(id=instance_id)
        if query.exists():
            raise TableNumberAlreadyExists(f"Table number '{number}' already exists.")

    @classmethod
    def create_table(cls, validated_data: dict) -> Table:
        """
        Creates a new table instance after performing all necessary validations.
        """
        capacity = validated_data.get('capacity')
        number = validated_data.get('number')

        cls._validate_common_table_fields(capacity, number)

        current_total_tables = Table.objects.count()
        if current_total_tables >= cls.RESTAURANT_MAX_TABLES:
            raise RestaurantCapacityFull(
                f"Restaurant is out of capacity and can't create a new table. Max tables allowed: {cls.RESTAURANT_MAX_TABLES}."
            )
        
        try:
            with transaction.atomic():
                table = Table.objects.create(**validated_data)
                return table
        except Exception as e:
            logger.error(f"Error creating table with data {validated_data}: {e}", exc_info=True)
            raise

    @classmethod
    def update_table(cls, instance: Table, validated_data: dict) -> Table:
        """
        Updates an existing table instance after performing all necessary validations.
        """
        capacity = validated_data.get('capacity', instance.capacity)
        number = validated_data.get('number', instance.number)

        cls._validate_common_table_fields(capacity, number, instance.id)
        
        try:
            with transaction.atomic():
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                return instance
        except Exception as e:
            logger.error(f"Error updating table ID {instance.id} with data {validated_data}: {e}", exc_info=True)
            raise

    @staticmethod
    def delete_table(instance: Table) -> None:
        """
        Deletes a table instance.
        Add business logic here if a table cannot be deleted under certain conditions (e.g., active reservations).
        """
        try:
            with transaction.atomic():
                instance.delete()
        except Exception as e:
            logger.error(f"Error deleting table ID {instance.id}: {e}", exc_info=True)
            raise

    @classmethod
    def find_suitable_tables_to_order(cls, party_size) -> List[Table]:
        all_tables = Table.objects.all()

        suitables_tables = []
        for table in all_tables:
            if table.capacity >= party_size:
                suitables_tables.append(table)

        return sorted(
            suitables_tables, 
            key=lambda table: table.capacity
        )
    