from rest_framework import serializers
from django.utils import timezone
from apps.shared.response.serializers import (
    CreatedResponseSerializer,
    SuccessResponseSerializer,
    PaginatedResponseSerializer,
)
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model with comprehensive field documentation.
    """

    def validate_quantity(self, value):
        """Ensure quantity is between 1 and 100"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        if value > 100:
            raise serializers.ValidationError("Quantity cannot exceed 100")
        return value

    def validate_menu_item(self, value):
        """Ensure menu_item exists"""
        if not value:
            raise serializers.ValidationError("Menu item is required")
        return value

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "menu_item",
            "menu_extra",
            "quantity",
            "notes",
            "is_delivered",
            "added_at",
        ]
        read_only_fields = ["id", "added_at"]
        extra_kwargs = {
            "menu_item": {
                "help_text": "Reference to the menu dish/item being ordered",
            },
            "menu_extra": {
                "help_text": "Optional menu extras/add-ons for the item",
                "required": False,
            },
            "quantity": {
                "help_text": "Number of items to order (between 1 and 100)",
                "min_value": 1,
                "max_value": 100,
            },
            "notes": {
                "help_text": "Special instructions or notes for the kitchen (e.g., no onions, well-done)",
                "required": False,
            },
            "is_delivered": {
                "help_text": "Whether this item has been delivered to the customer",
            },
        }


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model with comprehensive field documentation.
    """

    order_items = OrderItemSerializer(many=True, required=False)
    status_display = serializers.SerializerMethodField(
        help_text="Human-readable status label",
    )

    def get_status_display(self, obj):
        """Return the display name for the order status."""
        return dict(Order.STATUS_CHOICES).get(obj.status, obj.status)

    def validate_status(self, value):
        """Validate status choices"""
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value

    def validate_table(self, value):
        """Basic table validation"""
        if not value:
            raise serializers.ValidationError("Table is required")
        return value

    def validate(self, attrs):
        """Additional order-level validation"""
        if "end_at" in attrs and attrs["end_at"]:
            if hasattr(self, "instance") and self.instance and self.instance.created_at:
                if attrs["end_at"] < self.instance.created_at:
                    raise serializers.ValidationError(
                        "End time cannot be before creation time"
                    )
        return attrs

    def create(self, validated_data):
        """Handle nested order items creation"""
        order_items_data = validated_data.pop("order_items", [])
        order = Order.objects.create(**validated_data)

        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        """Handle order updates (without modifying order items in this basic implementation)"""
        order_items_data = validated_data.pop("order_items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = Order
        fields = [
            "id",
            "table",
            "status",
            "status_display",
            "created_at",
            "end_at",
            "order_items",
        ]
        read_only_fields = ["id", "created_at", "end_at", "status_display"]
        extra_kwargs = {
            "table": {
                "help_text": "Reference to the table this order belongs to",
            },
            "status": {
                "help_text": "Current status of the order (IN_PROGRESS, COMPLETED, or CANCELLED)",
            },
        }


# ============================================================================
# Order Response Serializers
# ============================================================================


class BaseSingleOrderResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single order."""

    data = OrderSerializer(
        help_text="Order details including items and status", required=True, many=False
    )

    class Meta:
        abstract = True


class BaseOrderListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple orders."""

    data = OrderSerializer(
        help_text="List of orders with items and status", required=True, many=True
    )

    class Meta:
        abstract = True


class CreateOrderResponseSerializer(
    CreatedResponseSerializer, BaseSingleOrderResponseSerializer
):
    """
    Response serializer for order creation (201 Created).

    Example:
        {
            "data": {
                "id": 1,
                "table": 1,
                "status": "IN_PROGRESS",
                "status_display": "In Progress",
                "created_at": "2024-01-01T12:00:00Z",
                "end_at": null,
                "order_items": []
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 201,
            "message": "Order successfully created",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for order creation",
        default="Order successfully created",
    )

    class Meta:
        ref_name = "CreateOrderResponse"


class UpdateOrderResponseSerializer(BaseSingleOrderResponseSerializer):
    """
    Response serializer for order update (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "table": 1,
                "status": "COMPLETED",
                "status_display": "Completed",
                "created_at": "2024-01-01T12:00:00Z",
                "end_at": "2024-01-01T13:00:00Z",
                "order_items": [...]
            },
            "timestamp": "2024-01-01T13:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Order successfully updated",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for order update",
        default="Order successfully updated",
    )

    class Meta:
        ref_name = "UpdateOrderResponse"


class RetrieveOrderResponseSerializer(BaseSingleOrderResponseSerializer):
    """
    Response serializer for single order retrieval (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "table": 1,
                "status": "IN_PROGRESS",
                "status_display": "In Progress",
                "created_at": "2024-01-01T12:00:00Z",
                "end_at": null,
                "order_items": [...]
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Order retrieved successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for order retrieval",
        default="Order retrieved successfully",
    )

    class Meta:
        ref_name = "RetrieveOrderResponse"


class ListOrderResponseSerializer(BaseOrderListResponseSerializer):
    """
    Response serializer for order list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "table": 1,
                    "status": "IN_PROGRESS",
                    "status_display": "In Progress",
                    "created_at": "2024-01-01T12:00:00Z",
                    "end_at": null,
                    "order_items": [...]
                },
                {
                    "id": 2,
                    "table": 2,
                    "status": "COMPLETED",
                    "status_display": "Completed",
                    "created_at": "2024-01-01T11:00:00Z",
                    "end_at": "2024-01-01T12:30:00Z",
                    "order_items": [...]
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Orders retrieved successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for orders list",
        default="Orders retrieved successfully",
    )

    class Meta:
        ref_name = "ListOrderResponse"


class PaginatedOrdersResponseSerializer(PaginatedResponseSerializer):
    """
    Response serializer for paginated order list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "table": 1,
                    "status": "IN_PROGRESS",
                    "status_display": "In Progress",
                    "created_at": "2024-01-01T12:00:00Z",
                    "end_at": null,
                    "order_items": [...]
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Orders page retrieved successfully",
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
        help_text="Success message for paginated orders",
        default="Orders page retrieved successfully",
    )

    class Meta:
        ref_name = "PaginatedOrdersResponse"


# ============================================================================
# OrderItem Response Serializers
# ============================================================================


class BaseSingleOrderItemResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single order item."""

    data = OrderItemSerializer(
        help_text="Order item details", required=True, many=False
    )

    class Meta:
        abstract = True


class BaseOrderItemListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple order items."""

    data = OrderItemSerializer(
        help_text="List of order items", required=True, many=True
    )

    class Meta:
        abstract = True


class CreateOrderItemResponseSerializer(
    CreatedResponseSerializer, BaseOrderItemListResponseSerializer
):
    """
    Response serializer for order items creation (201 Created).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "menu_item": 1,
                    "menu_extra": null,
                    "quantity": 2,
                    "notes": "No onions",
                    "is_delivered": false,
                    "added_at": "2024-01-01T12:00:00Z"
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 201,
            "message": "Items added to order successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for item creation",
        default="Items added to order successfully",
    )

    class Meta:
        ref_name = "CreateOrderItemResponse"


class ListOrderItemResponseSerializer(BaseOrderItemListResponseSerializer):
    """
    Response serializer for order items list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "menu_item": 1,
                    "menu_extra": null,
                    "quantity": 2,
                    "notes": "No onions",
                    "is_delivered": false,
                    "added_at": "2024-01-01T12:00:00Z"
                },
                {
                    "id": 2,
                    "menu_item": 2,
                    "menu_extra": 1,
                    "quantity": 1,
                    "notes": null,
                    "is_delivered": false,
                    "added_at": "2024-01-01T12:01:00Z"
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Order items retrieved successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for items list",
        default="Order items retrieved successfully",
    )

    class Meta:
        ref_name = "ListOrderItemResponse"
