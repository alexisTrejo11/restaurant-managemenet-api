from rest_framework import serializers
from decimal import Decimal
from apps.shared.response.serializers import (
    CreatedResponseSerializer,
    SuccessResponseSerializer,
    PaginatedResponseSerializer,
)
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
            "price": {
                "help_text": "Item price",
                "validators": [MinValueValidator(Decimal("0.00"))],
            },
            "quantity": {
                "help_text": "Item quantity",
                "validators": [MinValueValidator(1)],
            },
        }

    def validate(self, data):
        """Validate that the item has either an order_item or menu_item"""
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
    payment_method_display = serializers.SerializerMethodField(
        help_text="Human-readable payment method label",
    )
    payment_status_display = serializers.SerializerMethodField(
        help_text="Human-readable payment status label",
    )

    def get_payment_method_display(self, obj):
        """Return the display name for the payment method."""
        return dict(Payment.PAYMENT_METHODS).get(obj.payment_method, obj.payment_method)

    def get_payment_status_display(self, obj):
        """Return the display name for the payment status."""
        return dict(Payment.PAYMENT_STATUS).get(obj.payment_status, obj.payment_status)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "payment_method",
            "payment_method_display",
            "payment_status",
            "payment_status_display",
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
        read_only_fields = [
            "sub_total",
            "vat",
            "total",
            "created_at",
            "paid_at",
            "payment_method_display",
            "payment_status_display",
        ]
        extra_kwargs = {
            "order_id": {
                "help_text": "Related order ID",
                "required": False,
            },
            "payment_method": {
                "help_text": "Payment method (CASH, CARD, or TRANSACTION)",
            },
            "payment_status": {
                "help_text": "Payment status (PENDING, COMPLETED, REFUNDED, or CANCELLED)",
            },
            "discount": {
                "help_text": "Discount amount applied",
                "validators": [MinValueValidator(Decimal("0.00"))],
            },
            "vat_rate": {
                "help_text": "VAT rate as percentage (e.g., 16 for 16%)",
                "validators": [MinValueValidator(Decimal("0.00"))],
            },
            "currency_type": {
                "help_text": "Currency (MXN, USD, or EUR)",
            },
        }


# ============================================================================
# Payment Response Serializers
# ============================================================================


class BaseSinglePaymentResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single payment."""

    data = PaymentSerializer(
        help_text="Payment details including items and status",
        required=True,
        many=False,
    )

    class Meta:
        abstract = True


class BasePaymentListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple payments."""

    data = PaymentSerializer(
        help_text="List of payments with details",
        required=True,
        many=True,
    )

    class Meta:
        abstract = True


class CreatePaymentResponseSerializer(
    CreatedResponseSerializer, BaseSinglePaymentResponseSerializer
):
    """
    Response serializer for payment creation (201 Created).

    Example:
        {
            "data": {
                "id": 1,
                "order_id": 1,
                "payment_method": "CARD",
                "payment_method_display": "Card",
                "payment_status": "PENDING",
                "payment_status_display": "Pending",
                "sub_total": "100.00",
                "discount": "10.00",
                "vat_rate": "16.00",
                "vat": "16.00",
                "currency_type": "MXN",
                "total": "106.00",
                "created_at": "2024-01-01T12:00:00Z",
                "paid_at": null,
                "payment_items": []
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 201,
            "message": "Payment successfully created",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for payment creation",
        default="Payment successfully created",
    )

    class Meta:
        ref_name = "CreatePaymentResponse"


class UpdatePaymentResponseSerializer(BaseSinglePaymentResponseSerializer):
    """
    Response serializer for payment update (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "order_id": 1,
                "payment_method": "CARD",
                "payment_method_display": "Card",
                "payment_status": "COMPLETED",
                "payment_status_display": "Completed",
                "sub_total": "100.00",
                "discount": "10.00",
                "vat_rate": "16.00",
                "vat": "16.00",
                "currency_type": "MXN",
                "total": "106.00",
                "created_at": "2024-01-01T12:00:00Z",
                "paid_at": "2024-01-01T12:30:00Z",
                "payment_items": [...]
            },
            "timestamp": "2024-01-01T12:30:00Z",
            "success": true,
            "status_code": 200,
            "message": "Payment successfully updated",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for payment update",
        default="Payment successfully updated",
    )

    class Meta:
        ref_name = "UpdatePaymentResponse"


class RetrievePaymentResponseSerializer(BaseSinglePaymentResponseSerializer):
    """
    Response serializer for single payment retrieval (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "order_id": 1,
                "payment_method": "CARD",
                "payment_method_display": "Card",
                "payment_status": "COMPLETED",
                "payment_status_display": "Completed",
                "sub_total": "100.00",
                "discount": "10.00",
                "vat_rate": "16.00",
                "vat": "16.00",
                "currency_type": "MXN",
                "total": "106.00",
                "created_at": "2024-01-01T12:00:00Z",
                "paid_at": "2024-01-01T12:30:00Z",
                "payment_items": [...]
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Payment retrieved successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for payment retrieval",
        default="Payment retrieved successfully",
    )

    class Meta:
        ref_name = "RetrievePaymentResponse"


class ListPaymentResponseSerializer(BasePaymentListResponseSerializer):
    """
    Response serializer for payment list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "order_id": 1,
                    "payment_method": "CARD",
                    "payment_method_display": "Card",
                    "payment_status": "COMPLETED",
                    "payment_status_display": "Completed",
                    "sub_total": "100.00",
                    "discount": "10.00",
                    "vat_rate": "16.00",
                    "vat": "16.00",
                    "currency_type": "MXN",
                    "total": "106.00",
                    "created_at": "2024-01-01T12:00:00Z",
                    "paid_at": "2024-01-01T12:30:00Z",
                    "payment_items": [...]
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Payments retrieved successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for payments list",
        default="Payments retrieved successfully",
    )

    class Meta:
        ref_name = "ListPaymentResponse"


class PaginatedPaymentsResponseSerializer(PaginatedResponseSerializer):
    """
    Response serializer for paginated payment list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "order_id": 1,
                    "payment_method": "CARD",
                    "payment_method_display": "Card",
                    "payment_status": "COMPLETED",
                    "payment_status_display": "Completed",
                    "sub_total": "100.00",
                    "discount": "10.00",
                    "vat_rate": "16.00",
                    "vat": "16.00",
                    "currency_type": "MXN",
                    "total": "106.00",
                    "created_at": "2024-01-01T12:00:00Z",
                    "paid_at": "2024-01-01T12:30:00Z",
                    "payment_items": [...]
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Payments page retrieved successfully",
            "metadata": {
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_count": 150,
                    "total_pages": 8
                }
            }
        }
    """

    message = serializers.CharField(
        help_text="Success message for paginated payments",
        default="Payments page retrieved successfully",
    )

    class Meta:
        ref_name = "PaginatedPaymentsResponse"
