from ..models import StockItem
import logging
from django.db import transaction
from apps.shared.exceptions.custom_exceptions import BusinessRuleViolationException

logger = logging.getLogger(__name__)


class StockItemService:
    @classmethod
    def _validate_item_common_fields(
        cls, name: str, category: str, menu_item_id=None, item_id=None
    ):
        query = StockItem.objects.filter(name__iexact=name.strip())

        if item_id:
            query = query.exclude(id=item_id)

        if query.exists():
            raise BusinessRuleViolationException(
                "Item name already exists. Duplicate names not allowed"
            )

        if menu_item_id and category != "INGREDIENT":
            raise BusinessRuleViolationException(
                "Only ingredients can be linked to menu items"
            )

    @classmethod
    def create_stock_item(cls, validated_data: dict) -> StockItem:
        name = validated_data.get("name")
        category = validated_data.get("category")
        menu_item = validated_data.get("menu_item")
        menu_item_id = menu_item.id if menu_item else None

        cls._validate_item_common_fields(name, category, menu_item_id)

        try:
            with transaction.atomic():
                stock_item = StockItem.objects.create(**validated_data)
                return stock_item
        except Exception as e:
            logger.error(
                f"Error creating stockn item with data {validated_data}: {e}",
                exc_info=True,
            )
            raise

    @classmethod
    def update_stock_item(cls, validated_data: dict, item: StockItem) -> StockItem:
        name = validated_data.get("name")
        category = validated_data.get("category")
        menu_item = validated_data.get("menu_item")
        menu_item_id = menu_item.id if menu_item else None

        cls._validate_item_common_fields(name, category, menu_item_id, item.id)

        try:
            with transaction.atomic():
                for field, value in validated_data.items():
                    setattr(item, field, value)

                item.full_clean()
                item.save()

                return item
        except Exception as e:
            logger.error(
                f"Error updating stock item with data {validated_data}: {e}",
                exc_info=True,
            )
            raise

    @classmethod
    def delete_stock_item(cls, item: StockItem) -> None:
        try:
            with transaction.atomic():
                item.delete()
        except Exception as e:
            logger.error(f"Error deleting table ID {item.id}: {e}", exc_info=True)
            raise
