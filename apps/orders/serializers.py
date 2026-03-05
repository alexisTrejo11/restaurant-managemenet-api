from rest_framework import serializers
from django.utils import timezone
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
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


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ["id", "table", "status", "created_at", "end_at", "order_items"]
        read_only_fields = ["id", "created_at", "end_at"]

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
            if "created_at" in self.instance and self.instance.created_at:
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
