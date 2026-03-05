from ..models import Payment, PaymentItem
from apps.orders.models import OrderItem
from decimal import Decimal
from typing import List, Dict, Optional
from .payment_calculator_service import PaymentCalculatorService as CalculatorService


class PaymentItemService:
    """Service class for handling payment item generation and operations."""

    @classmethod
    def generate_items_from_order(
        cls, order_items: List[OrderItem], payment: Payment
    ) -> List[PaymentItem]:
        """
        Generate PaymentItems from OrderItems, grouping by menu_item.id.

        Args:
            order_items: List of OrderItems to process
            payment: Payment object to associate with the items

        Returns:
            List of generated PaymentItems (not yet saved to database)
        """
        grouped_items = {}

        for order_item in order_items:
            menu_item = order_item.menu_item

            if menu_item.id not in grouped_items:
                grouped_items[menu_item.id] = cls._generate_item_from_order(
                    payment, order_item
                )
            else:
                cls._increase_item_values(grouped_items[menu_item.id], order_item)

        return list(grouped_items.values())

    @classmethod
    def generate_items(
        cls, payment: Payment, items_data: List[Dict]
    ) -> List[PaymentItem]:
        """
        Generate PaymentItems from raw item data.

        Args:
            payment: Payment object to associate with items
            items_data: List of dictionaries containing item data

        Returns:
            List of generated PaymentItems
        """
        payment_items = []

        for item in items_data:
            order_item = item.get("order_item")
            menu_item = item.get("menu_item")

            if order_item and menu_item:
                payment_item = cls._generate_item_from_order(payment, order_item)
            else:
                payment_item = cls._generate_item_from_data(payment, item)

            payment_items.append(payment_item)

        return payment_items

    @classmethod
    def save_items(cls, payment_items: List[PaymentItem]) -> None:
        """
        Save payment items to database in bulk.

        Args:
            payment_items: List of PaymentItems to save
        """
        if not payment_items:
            return

        new_items = [item for item in payment_items if item.id is None]
        existing_items = [item for item in payment_items if item.id is not None]

        if new_items:
            PaymentItem.objects.bulk_create(new_items)

        if existing_items:
            PaymentItem.objects.bulk_update(
                existing_items, fields=["quantity", "extras_charges", "total"]
            )

    @classmethod
    def _generate_item_from_order(
        cls, payment: Payment, order_item: OrderItem
    ) -> PaymentItem:
        """
        Create a PaymentItem from an OrderItem.

        Args:
            payment: Associated Payment object
            order_item: OrderItem to convert

        Returns:
            Generated PaymentItem
        """
        menu_item = order_item.menu_item
        menu_extra = order_item.menu_extra

        base_price = CalculatorService.calculate_item_base_price(
            menu_item.price, order_item.quantity
        )
        extras_price = CalculatorService.calculate_menu_extra_charges(menu_extra)
        item_total = CalculatorService.calculate_item_total_price(
            base_price, extras_price
        )

        return PaymentItem(
            payment=payment,
            order_item=order_item,
            menu_item=menu_item,
            menu_item_extra=menu_extra,
            quantity=order_item.quantity,
            price=menu_item.price,
            extras_charges=extras_price,
            total=item_total,
            charge_description=menu_item.name,
        )

    @classmethod
    def _generate_item_from_data(cls, payment: Payment, item_data: Dict) -> PaymentItem:
        """
        Create a PaymentItem from raw data dictionary.

        Args:
            payment: Associated Payment object
            item_data: Dictionary containing item data

        Returns:
            Generated PaymentItem
        """
        extras_charges = item_data.get("extra_charges", Decimal("0.00"))
        total_price = CalculatorService.calculate_item_total_price(
            item_data["price"], extras_charges
        )

        return PaymentItem(
            payment=payment,
            quantity=item_data["quantity"],
            price=item_data["price"],
            extras_charges=extras_charges,
            total=total_price,
            charge_description=item_data.get("charge_description", ""),
        )

    @classmethod
    def _increase_item_values(
        cls, existing_item: PaymentItem, order_item: OrderItem
    ) -> None:
        """
        Increase quantity and prices of an existing PaymentItem.

        Args:
            existing_item: PaymentItem to update
            order_item: OrderItem containing update values
        """
        menu_item = order_item.menu_item
        menu_extra = order_item.menu_extra

        base_price = CalculatorService.calculate_item_base_price(
            menu_item.price, order_item.quantity
        )
        extras_price = CalculatorService.calculate_menu_extra_charges(menu_extra)
        item_total = CalculatorService.calculate_item_total_price(
            base_price, extras_price
        )

        existing_item.quantity += order_item.quantity
        existing_item.extras_charges += extras_price
        existing_item.total += item_total
