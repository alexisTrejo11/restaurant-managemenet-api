from typing import List
from django.db import transaction
from ..models import OrderItem, Order
from apps.shared.exceptions.custom_exceptions import (
    BusinessRuleViolationException,
    EntityNotFoundException,
)
import logging

logger = logging.getLogger(__name__)


class OrderItemService:
    MAX_ALLOWED_ITEMS_PER_REQUEST = 10

    @classmethod
    def add_items(cls, order: Order, items_validated_data: List) -> Order:
        """
        Adds multiple items to an order with validation and atomic transaction

        Args:
            order: The Order instance to add items to
            items_validated_data: List of validated item data dictionaries

        Returns:
            The updated Order instance

        Raises:
            BusinessRuleViolationException: If item limits are exceeded
        """
        cls._validate_item_length_limit(items_validated_data)
        cls._validate_active_order(order)

        try:
            with transaction.atomic():
                items = cls._generate_items(order, items_validated_data)
                OrderItem.objects.bulk_create(items)
                order.refresh_from_db()
                return order
        except Exception as e:
            logger.error(
                f"Error adding items to order {order.id}: {str(e)}", exc_info=True
            )
            raise

    @classmethod
    def set_item_as_delivered(cls, order: Order, items_ids: List[int]):
        items = cls._get_items_by_order_and_ids(order, items_ids)
        for item in items:
            item.set_as_delivered()

        OrderItem.objects.bulk_update(items)

    @classmethod
    def delete_items(cls, order: Order, items_ids: List[int]) -> None:
        """
        Deletes multiple items from an order with validation

        Args:
            order: The Order instance
            items_ids: List of item IDs to delete

        Raises:
            EntityNotFoundException: If any item is not found
        """
        with transaction.atomic():
            existing_items = cls._get_items_by_order_and_ids(order, items_ids)
            existing_items.delete()

    @classmethod
    def _generate_items(cls, order: Order, items_data: List[dict]) -> List[OrderItem]:
        """
        Generates OrderItem instances from validated data

        Args:
            order: The Order instance
            items_data: List of validated item data dictionaries

        Returns:
            List of unsaved OrderItem instances
        """
        return [
            OrderItem(
                order=order,
                menu_item=item["menu_item"],
                quantity=item.get("quantity", 1),
                notes=item.get("notes", ""),
                is_delivered=False,
            )
            for item in items_data
        ]

    @classmethod
    def _validate_item_length_limit(cls, items: List) -> None:
        """
        Validates the number of items doesn't exceed the maximum allowed

        Args:
            items: List of items to validate

        Raises:
            BusinessRuleViolationException: If limit is exceeded
        """
        if len(items) > cls.MAX_ALLOWED_ITEMS_PER_REQUEST:
            raise BusinessRuleViolationException(
                f"Cannot process more than {cls.MAX_ALLOWED_ITEMS_PER_REQUEST} items at once"
            )

    @classmethod
    def _validate_active_order(cls, order: Order):
        if order.status != "IN_PROGRESS":
            raise BusinessRuleViolationException(f"Order Finished Can't Add any item")

    @classmethod
    def _get_items_by_order_and_ids(cls, order: Order, items_ids: List[int]):
        existing_items = OrderItem.objects.filter(id__in=items_ids, order=order)

        if existing_items.count() != len(items_ids):
            found_ids = set(existing_items.values_list("id", flat=True))
            missing_ids = set(items_ids) - found_ids
            raise EntityNotFoundException(
                f"Order Items {list(missing_ids)} not found in order {order.id}",
            )
        return existing_items
