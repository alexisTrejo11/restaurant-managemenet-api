from rest_framework import serializers
from decimal import Decimal
from apps.shared.response.serializers import (
    CreatedResponseSerializer,
    SuccessResponseSerializer,
    PaginatedResponseSerializer,
)
from .models import Dish
from .services import DishService
from django.core.exceptions import ValidationError


class DishSerializer(serializers.ModelSerializer):
    """
    Serializer for Dish model with comprehensive field documentation.
    """

    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    category_display = serializers.SerializerMethodField(
        help_text="Human-readable category label",
    )
    status_display = serializers.SerializerMethodField(
        help_text="Human-readable status label",
    )

    def get_category_display(self, obj):
        """Return the display name for the dish category."""
        return dict(Dish.CATEGORY_CHOICES).get(obj.category, obj.category)

    def get_status_display(self, obj):
        """Return the display name for the dish status."""
        return dict(Dish.STATUS_CHOICES).get(obj.status, obj.status)

    def validate(self, attrs):
        """Cross-field validation between status and price"""
        if attrs.get("status") == "INACTIVE" and attrs.get("price", 0) > 100000:
            raise serializers.ValidationError(
                {"price": "Inactive items cannot have price > 100,000"}
            )
        return attrs

    def validate_name(self, value):
        """Validate and normalize dish name"""
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long")
        return value.title()

    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= Decimal("0.00"):
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_category(self, value):
        """Validate category is valid (case-insensitive)"""
        return DishService.validate_category(value.upper())

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update a menu item with business logic validation"""
        try:
            return DishService.update_menu_item(instance, **validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

    class Meta:
        model = Dish
        fields = [
            "id",
            "image",
            "name",
            "price",
            "description",
            "category",
            "category_display",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "category_display",
            "status_display",
        ]
        extra_kwargs = {
            "name": {
                "help_text": "Dish name (minimum 3 characters, will be title-cased)",
                "trim_whitespace": True,
                "min_length": 3,
                "max_length": 255,
            },
            "price": {
                "help_text": "Dish price in decimal format (must be greater than 0)",
                "min_value": Decimal("0.01"),
            },
            "image": {
                "help_text": "URL or path to dish image",
                "max_length": 255,
                "required": False,
            },
            "description": {
                "help_text": "Detailed description of the dish (optional)",
                "trim_whitespace": True,
                "allow_blank": True,
                "required": False,
                "max_length": 255,
            },
            "category": {
                "help_text": "Dish category (DRINKS, ALCOHOL_DRINKS, BREAKFASTS, STARTERS, MEALS, DESSERTS, or EXTRAS)",
            },
            "status": {
                "help_text": "Dish status (ACTIVE, INACTIVE, or DRAFT)",
            },
        }


# ============================================================================
# Dish Response Serializers
# ============================================================================


class BaseSingleDishResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single dish."""

    data = DishSerializer(
        help_text="Dish details including category and status",
        required=True,
        many=False,
    )

    class Meta:
        abstract = True


class BaseDishListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple dishes."""

    data = DishSerializer(
        help_text="List of dishes with details", required=True, many=True
    )

    class Meta:
        abstract = True


class CreateDishResponseSerializer(
    CreatedResponseSerializer, BaseSingleDishResponseSerializer
):
    """
    Response serializer for dish creation (201 Created).

    Example:
        {
            "data": {
                "id": 1,
                "name": "Grilled Salmon",
                "price": "25.50",
                "category": "MEALS",
                "category_display": "Meals",
                "status": "ACTIVE",
                "status_display": "Active",
                "image": "https://example.com/images/salmon.jpg",
                "description": "Fresh Atlantic salmon grilled with lemon and herbs",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 201,
            "message": "Dish Grilled Salmon successfully created",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for dish creation",
        default="Dish successfully created",
    )

    class Meta:
        ref_name = "CreateDishResponse"


class UpdateDishResponseSerializer(BaseSingleDishResponseSerializer):
    """
    Response serializer for dish update (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "name": "Grilled Salmon",
                "price": "28.50",
                "category": "MEALS",
                "category_display": "Meals",
                "status": "ACTIVE",
                "status_display": "Active",
                "image": "https://example.com/images/salmon.jpg",
                "description": "Fresh Atlantic salmon grilled with lemon and herbs",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T13:00:00Z"
            },
            "timestamp": "2024-01-01T13:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Dish Grilled Salmon successfully updated",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for dish update",
        default="Dish successfully updated",
    )

    class Meta:
        ref_name = "UpdateDishResponse"


class RetrieveDishResponseSerializer(BaseSingleDishResponseSerializer):
    """
    Response serializer for single dish retrieval (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "name": "Grilled Salmon",
                "price": "25.50",
                "category": "MEALS",
                "category_display": "Meals",
                "status": "ACTIVE",
                "status_display": "Active",
                "image": "https://example.com/images/salmon.jpg",
                "description": "Fresh Atlantic salmon grilled with lemon and herbs",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Dish retrieved successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for dish retrieval",
        default="Dish retrieved successfully",
    )

    class Meta:
        ref_name = "RetrieveDishResponse"


class ListDishResponseSerializer(BaseDishListResponseSerializer):
    """
    Response serializer for dish list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "name": "Grilled Salmon",
                    "price": "25.50",
                    "category": "MEALS",
                    "category_display": "Meals",
                    "status": "ACTIVE",
                    "status_display": "Active",
                    "image": "https://example.com/images/salmon.jpg",
                    "description": "Fresh Atlantic salmon grilled with lemon and herbs",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z"
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Dishes retrieved successfully",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message for dishes list",
        default="Dishes retrieved successfully",
    )

    class Meta:
        ref_name = "ListDishResponse"


class PaginatedDishesResponseSerializer(PaginatedResponseSerializer):
    """
    Response serializer for paginated dish list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "name": "Grilled Salmon",
                    "price": "25.50",
                    "category": "MEALS",
                    "category_display": "Meals",
                    "status": "ACTIVE",
                    "status_display": "Active",
                    "image": "https://example.com/images/salmon.jpg",
                    "description": "Fresh Atlantic salmon grilled with lemon and herbs",
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z"
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Dishes page retrieved successfully",
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
        help_text="Success message for paginated dishes",
        default="Dishes page retrieved successfully",
    )

    class Meta:
        ref_name = "PaginatedDishesResponse"
