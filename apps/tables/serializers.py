from rest_framework import serializers
from apps.shared.response.serializers import (
    CreatedResponseSerializer,
    SuccessResponseSerializer,
    PaginatedResponseSerializer,
)
from .models import Table


class TableSerializer(serializers.ModelSerializer):
    """
    Serializer for Table model with comprehensive field documentation.
    """

    def validate_capacity(self, value):
        """Validate table capacity is within acceptable range."""
        if value < 1:
            raise serializers.ValidationError("Capacity must be at least 1.")
        if value > 20:
            raise serializers.ValidationError("Maximum capacity is 20.")
        return value

    def validate_number(self, value):
        """Validate table number format and uniqueness."""
        if not value:
            raise serializers.ValidationError("Table number cannot be empty.")
        return value

    class Meta:
        model = Table
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "number": {
                "help_text": "Unique table identifier (e.g., T-01, B-02) - format: Letter-Number",
                "max_length": 10,
                "error_messages": {
                    "unique": "A table with this number already exists.",
                    "invalid": "Invalid table number format. Use format like T-01, B-02, etc.",
                },
            },
            "capacity": {
                "help_text": "Number of seats (must be between 1 and 20)",
                "min_value": 1,
                "max_value": 20,
            },
            "is_available": {
                "help_text": "Current availability status",
            },
        }


class BaseSingleTableResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single table."""

    data = TableSerializer(help_text="Table details", required=True, many=False)

    class Meta:
        abstract = True  # Prevents this from being registered as a serializer


class BaseTableListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple tables."""

    data = TableSerializer(help_text="List of tables", required=True, many=True)

    class Meta:
        abstract = True


class CreateTableResponseSerializer(
    CreatedResponseSerializer, BaseSingleTableResponseSerializer
):
    """
    Response serializer for table creation (201 Created).

    Example:
        {
            "data": {
                "id": 1,
                "number": "T-42",
                "capacity": 4,
                "is_available": true,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 201,
            "message": "Table T-42 successfully created",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message with table identifier",
        default="Table successfully created",
    )

    class Meta:
        ref_name = "CreateTableResponse"


class UpdateTableResponseSerializer(BaseSingleTableResponseSerializer):
    """
    Response serializer for table update (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "number": "T-42",
                "capacity": 6,
                "is_available": false,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T13:00:00Z"
            },
            "timestamp": "2024-01-01T13:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Table T-42 successfully updated",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message with table identifier",
        default="Table successfully updated",
    )

    class Meta:
        ref_name = "UpdateTableResponse"


class FoundTableResponseSerializer(BaseSingleTableResponseSerializer):
    """
    Response serializer for single table retrieval (200 OK).

    Example:
        {
            "data": {
                "id": 1,
                "number": "T-42",
                "capacity": 4,
                "is_available": true,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            },
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Table T-42 successfully retrieved",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message with table identifier",
        default="Table successfully retrieved",
    )

    class Meta:
        ref_name = "FoundTableResponse"


class FoundTableListResponseSerializer(BaseTableListResponseSerializer):
    """
    Response serializer for multiple tables retrieval (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "number": "T-42",
                    "capacity": 4,
                    "is_available": true,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z"
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Tables successfully retrieved",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="Tables successfully retrieved",
    )

    class Meta:
        ref_name = "FoundTableListResponse"


class PaginatedTablesResponseSerializer(PaginatedResponseSerializer):
    """
    Response serializer for paginated table list (200 OK).

    Example:
        {
            "data": [
                {
                    "id": 1,
                    "number": "T-42",
                    "capacity": 4,
                    "is_available": true,
                    "created_at": "2024-01-01T12:00:00Z",
                    "updated_at": "2024-01-01T12:00:00Z"
                }
            ],
            "timestamp": "2024-01-01T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Tables successfully retrieved",
            "metadata": {
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_count": 50,
                    "total_pages": 3,
                    "has_next": true,
                    "has_previous": false
                }
            }
        }
    """

    data = TableSerializer(
        help_text="Paginated list of tables", required=True, many=True
    )

    message = serializers.CharField(
        help_text="Success message",
        default="Tables successfully retrieved",
    )

    class Meta:
        ref_name = "PaginatedTablesResponse"
