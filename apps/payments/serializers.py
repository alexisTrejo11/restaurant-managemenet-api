from rest_framework import serializers
from decimal import Decimal
from .models import Payment, PaymentItem
from apps.orders.models import Order
from django.core.validators import MinValueValidator


class PaymentItemSerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentItem with read-only calculated fields
    """

    class Meta:
        model = PaymentItem
        fields = [
            "id",
            "order_item",
            "menu_item",
            "menu_item_extra",
            "price",
            "quantity",
            "extras_charges",
            "total",
            "charge_description",
        ]
        read_only_fields = ["total", "extras_charges"]
        extra_kwargs = {
            "price": {"validators": [MinValueValidator(Decimal("0.00"))]},
            "quantity": {"validators": [MinValueValidator(1)]},
        }

    def validate(self, data):
        """
        Validate that the item has either an order_item or menu_item
        """
        if not data.get("order_item") and not data.get("menu_item"):
            raise serializers.ValidationError(
                "Payment item must have either an order_item or menu_item"
            )
        return data


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for Payment with calculated fields and nested payment items
    """

    payment_items = PaymentItemSerializer(many=True, required=False)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(), source="order", required=False, allow_null=True
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "payment_method",
            "payment_status",
            "sub_total",
            "discount",
            "vat_rate",
            "vat",
            "currency_type",
            "total",
            "created_at",
            "paid_at",
            "payment_items",
        ]
        read_only_fields = ["sub_total", "vat", "total", "created_at", "paid_at"]
        extra_kwargs = {
            "discount": {"validators": [MinValueValidator(Decimal("0.00"))]},
            "vat_rate": {"validators": [MinValueValidator(Decimal("0.00"))]},
        }
