from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from apps.shared.response.serializers import (
    CreatedResponseSerializer,
    SuccessResponseSerializer,
    PaginatedResponseSerializer,
)
from .models import StockItem, Stock, StockTransaction


# ===========================
# Core Serializers
# ===========================


class StockItemSerializer(serializers.ModelSerializer):
    """
    Serializer for StockItem model with comprehensive field documentation.

    Used for managing inventory items (ingredients, utensils, containers, etc).
    """

    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True,
        help_text=_("Human-readable category name"),
    )

    class Meta:
        model = StockItem
        fields = [
            "id",
            "name",
            "unit",
            "category",
            "category_display",
            "menu_item",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "category_display"]
        extra_kwargs = {
            "name": {
                "min_length": 2,
                "max_length": 255,
                "help_text": _("Descriptive name of the inventory item"),
                "error_messages": {
                    "min_length": _("Name must be at least 2 characters long"),
                    "max_length": _("Name cannot exceed 255 characters"),
                },
            },
            "unit": {
                "min_length": 1,
                "max_length": 10,
                "help_text": _("Measurement unit (kg, lb, units, liters, etc)"),
                "error_messages": {
                    "min_length": _("Unit must be at least 1 character"),
                    "max_length": _("Unit cannot exceed 10 characters"),
                },
            },
            "category": {
                "help_text": _(
                    "Item classification (INGREDIENT, UTENSIL, CONTAINER, OTHER)"
                ),
            },
            "menu_item": {
                "help_text": _("Related menu item (for ingredients only)"),
                "required": False,
            },
        }

    def validate_name(self, value):
        """Case-insensitive name validation"""
        if StockItem.objects.filter(name__iexact=value).exists():
            if self.instance and self.instance.name.lower() == value.lower():
                return value
            raise serializers.ValidationError(
                _("A stock item with this name already exists")
            )
        return value.strip()

    def validate(self, data):
        """Cross-field validation"""
        if data.get("menu_item") and data.get("category") != "INGREDIENT":
            raise serializers.ValidationError(
                {"menu_item": _("Only ingredients can be linked to menu items")}
            )
        return data


class StockTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for StockTransaction model with comprehensive documentation.

    Handles stock IN and OUT transactions with automatic validation.
    """

    stock_item_name = serializers.CharField(
        source="stock.item.name",
        read_only=True,
        help_text=_("Name of the related stock item"),
    )

    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display",
        read_only=True,
        help_text=_("Readable transaction type"),
    )

    class Meta:
        model = StockTransaction
        fields = [
            "id",
            "stock",
            "stock_item_name",
            "quantity",
            "transaction_type",
            "transaction_type_display",
            "date",
            "expires_at",
            "employee",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "stock_item_name",
            "transaction_type_display",
            "created_at",
        ]
        extra_kwargs = {
            "stock": {
                "help_text": _("ID of the stock to transact"),
            },
            "quantity": {
                "min_value": 1,
                "max_value": 10000,
                "help_text": _("Quantity for this transaction (1-10000)"),
                "validators": [MinValueValidator(1, _("Quantity must be at least 1"))],
                "error_messages": {
                    "invalid": _("Enter a valid number"),
                    "min_value": _("Quantity cannot be less than 1"),
                    "max_value": _("Quantity cannot exceed 10,000"),
                },
            },
            "transaction_type": {
                "help_text": _("Transaction type: IN (stock in) or OUT (stock out)"),
            },
            "date": {
                "help_text": _("When the transaction occurred"),
            },
            "expires_at": {
                "required": False,
                "allow_null": True,
                "help_text": _("Optional expiration date for incoming stock"),
            },
            "employee": {
                "required": False,
                "allow_null": True,
                "help_text": _("User ID of employee who processed the transaction"),
            },
            "notes": {
                "required": False,
                "allow_blank": True,
                "max_length": 500,
                "help_text": _("Additional transaction details (optional)"),
            },
        }

    def validate_quantity(self, value):
        """Context-aware quantity validation"""
        if self.context.get("request") and self.context["request"].method in [
            "POST",
            "PUT",
            "PATCH",
        ]:
            stock = self.initial_data.get("stock")
            transaction_type = self.initial_data.get("transaction_type")

            if transaction_type == "OUT" and stock:
                current_stock = Stock.objects.get(pk=stock).total_stock
                if value > current_stock:
                    raise serializers.ValidationError(
                        _("Cannot withdraw more than available stock")
                    )
        return value

    def validate_expires_at(self, value):
        """Future date validation"""
        if value and value < timezone.now():
            raise serializers.ValidationError(
                _("Expiration date must be in the future")
            )
        return value

    def create(self, validated_data):
        """Auto-update stock levels on transaction creation"""
        transaction = super().create(validated_data)

        stock = transaction.stock
        if transaction.transaction_type == "IN":
            stock.total_stock += transaction.quantity
        else:
            stock.total_stock -= transaction.quantity
        stock.save()

        return transaction


class StockSerializer(serializers.ModelSerializer):
    """
    Serializer for Stock model with nested transactions support.

    Includes optional transaction history when requested.
    """

    transactions = serializers.SerializerMethodField(
        help_text=_(
            "A list of transactions associated with this stock. Included only if include_transactions=true in query params."
        )
    )
    item_id = serializers.PrimaryKeyRelatedField(
        source="item",
        queryset=StockItem.objects.all(),
        error_messages={
            "does_not_exist": _("The specified inventory item does not exist."),
            "incorrect_type": _("The item ID must be an integer."),
        },
        help_text=_("ID of the inventory item associated with this stock record"),
    )
    item_name = serializers.CharField(
        source="item.name",
        read_only=True,
        help_text=_("Name of the stock item"),
    )

    class Meta:
        model = Stock
        fields = [
            "id",
            "item_id",
            "item_name",
            "total_stock",
            "optimal_stock_quantity",
            "created_at",
            "updated_at",
            "transactions",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "transactions",
            "item_name",
        ]
        extra_kwargs = {
            "total_stock": {
                "min_value": 0,
                "max_value": 1000000,
                "help_text": _("Current total quantity in inventory (0-1,000,000)"),
                "error_messages": {
                    "invalid": _("Stock must be an integer."),
                    "max_value": _("Stock cannot exceed 1,000,000."),
                    "min_value": _("Stock cannot be negative."),
                },
                "validators": [MinValueValidator(0), MaxValueValidator(1_000_000)],
            },
            "optimal_stock_quantity": {
                "min_value": 1,
                "max_value": 1000000,
                "help_text": _("Ideal quantity to maintain (1-1,000,000)"),
                "error_messages": {
                    "invalid": _("Optimal quantity must be an integer."),
                    "max_value": _("Optimal quantity cannot exceed 1,000,000."),
                    "min_value": _("Optimal quantity must be at least 1."),
                },
                "validators": [MinValueValidator(1), MaxValueValidator(1_000_000)],
            },
        }

    def get_transactions(self, obj):
        """Includes transactions only if explicitly requested"""
        request = self.context.get("request")
        if (
            request
            and request.query_params.get("include_transactions", "").lower() == "true"
        ):
            return StockTransactionSerializer(
                obj.get_transactions(), many=True, context=self.context
            ).data
        return None

    def validate(self, data):
        """Cross-field validation"""
        total_stock = data.get(
            "total_stock",
            getattr(self.instance, "total_stock", 0) if self.instance else 0,
        )
        optimal_stock_quantity = data.get(
            "optimal_stock_quantity",
            getattr(self.instance, "optimal_stock_quantity", 1) if self.instance else 1,
        )

        if total_stock > optimal_stock_quantity * 3:
            raise serializers.ValidationError(
                {"total_stock": _("Cannot be more than 3x the optimal quantity.")}
            )
        return data

    def create(self, validated_data):
        """Override to protect auto-generated fields"""
        validated_data.pop("created_at", None)
        validated_data.pop("updated_at", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Override to protect auto-generated fields"""
        validated_data.pop("created_at", None)
        validated_data.pop("updated_at", None)
        return super().update(instance, validated_data)


# ===========================
# Response Serializers
# ===========================


# Stock Item Response Serializers


class BaseSingleStockItemResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single stock item."""

    data = StockItemSerializer(
        help_text=_("Stock item details"), required=True, many=False
    )

    class Meta:
        abstract = True


class BaseStockItemListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple stock items."""

    data = StockItemSerializer(
        help_text=_("List of stock items"), required=True, many=True
    )

    class Meta:
        abstract = True


class CreateStockItemResponseSerializer(
    CreatedResponseSerializer, BaseSingleStockItemResponseSerializer
):
    """Response serializer for stock item creation (201 Created)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock item successfully created",
    )

    class Meta:
        ref_name = "CreateStockItemResponse"


class UpdateStockItemResponseSerializer(BaseSingleStockItemResponseSerializer):
    """Response serializer for stock item update (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock item successfully updated",
    )

    class Meta:
        ref_name = "UpdateStockItemResponse"


class RetrieveStockItemResponseSerializer(BaseSingleStockItemResponseSerializer):
    """Response serializer for single stock item retrieval (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock item successfully retrieved",
    )

    class Meta:
        ref_name = "RetrieveStockItemResponse"


class ListStockItemResponseSerializer(BaseStockItemListResponseSerializer):
    """Response serializer for multiple stock items retrieval (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock items successfully retrieved",
    )

    class Meta:
        ref_name = "ListStockItemResponse"


class PaginatedStockItemResponseSerializer(PaginatedResponseSerializer):
    """Response serializer for paginated stock item list (200 OK)."""

    data = StockItemSerializer(
        help_text=_("Paginated list of stock items"), required=True, many=True
    )

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock items successfully retrieved",
    )

    class Meta:
        ref_name = "PaginatedStockItemResponse"


# Stock Response Serializers


class BaseSingleStockResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single stock."""

    data = StockSerializer(help_text=_("Stock details"), required=True, many=False)

    class Meta:
        abstract = True


class BaseStockListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple stocks."""

    data = StockSerializer(help_text=_("List of stocks"), required=True, many=True)

    class Meta:
        abstract = True


class CreateStockResponseSerializer(
    CreatedResponseSerializer, BaseSingleStockResponseSerializer
):
    """Response serializer for stock creation (201 Created)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock successfully created",
    )

    class Meta:
        ref_name = "CreateStockResponse"


class UpdateStockResponseSerializer(BaseSingleStockResponseSerializer):
    """Response serializer for stock update (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock successfully updated",
    )

    class Meta:
        ref_name = "UpdateStockResponse"


class RetrieveStockResponseSerializer(BaseSingleStockResponseSerializer):
    """Response serializer for single stock retrieval (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stock successfully retrieved",
    )

    class Meta:
        ref_name = "RetrieveStockResponse"


class ListStockResponseSerializer(BaseStockListResponseSerializer):
    """Response serializer for multiple stocks retrieval (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stocks successfully retrieved",
    )

    class Meta:
        ref_name = "ListStockResponse"


class PaginatedStockResponseSerializer(PaginatedResponseSerializer):
    """Response serializer for paginated stock list (200 OK)."""

    data = StockSerializer(
        help_text=_("Paginated list of stocks"), required=True, many=True
    )

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Stocks successfully retrieved",
    )

    class Meta:
        ref_name = "PaginatedStockResponse"


# Stock Transaction Response Serializers


class BaseSingleTransactionResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single transaction."""

    data = StockTransactionSerializer(
        help_text=_("Transaction details"), required=True, many=False
    )

    class Meta:
        abstract = True


class BaseTransactionListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple transactions."""

    data = StockTransactionSerializer(
        help_text=_("List of transactions"), required=True, many=True
    )

    class Meta:
        abstract = True


class CreateTransactionResponseSerializer(
    CreatedResponseSerializer, BaseSingleTransactionResponseSerializer
):
    """Response serializer for transaction creation (201 Created)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Transaction successfully created",
    )

    class Meta:
        ref_name = "CreateTransactionResponse"


class UpdateTransactionResponseSerializer(BaseSingleTransactionResponseSerializer):
    """Response serializer for transaction update (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Transaction successfully updated",
    )

    class Meta:
        ref_name = "UpdateTransactionResponse"


class RetrieveTransactionResponseSerializer(BaseSingleTransactionResponseSerializer):
    """Response serializer for single transaction retrieval (200 OK)."""

    message = serializers.CharField(
        help_text=_("Success message"),
        default="Transaction successfully retrieved",
    )

    class Meta:
        ref_name = "RetrieveTransactionResponse"
