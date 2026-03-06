from rest_framework import serializers
from apps.shared.response.serializers import (
    CreatedResponseSerializer,
    SuccessResponseSerializer,
    PaginatedResponseSerializer,
)
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for Reservation model with comprehensive field documentation.

    Handles validation and serialization of restaurant table reservations.
    """

    status_display = serializers.CharField(
        source="get_status_display",
        read_only=True,
        help_text="Human-readable status name",
    )

    class Meta:
        model = Reservation
        fields = [
            "id",
            "name",
            "phone_number",
            "customer_number",
            "email",
            "table",
            "reservation_date",
            "status",
            "status_display",
            "created_at",
            "cancelled_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "cancelled_at",
            "status",
            "status_display",
        ]
        extra_kwargs = {
            "name": {
                "min_length": 2,
                "max_length": 255,
                "help_text": "Customer's full name",
            },
            "phone_number": {
                "max_length": 255,
                "help_text": "Customer's contact phone number",
            },
            "customer_number": {
                "min_value": 1,
                "max_value": 100,
                "help_text": "Number of people for this reservation (1-100)",
            },
            "email": {
                "required": True,
                "help_text": "Customer's email address",
            },
            "table": {
                "help_text": "Table to reserve (by table number)",
            },
            "reservation_date": {
                "required": True,
                "help_text": "Reservation date and time (must be in future)",
            },
        }

    def validate_email(self, value):
        """Validate email format."""
        try:
            serializers.EmailField().to_internal_value(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_phone_number(self, value):
        """Validate phone number format."""
        if not all(char.isdigit() or char in "+-() " for char in value):
            raise serializers.ValidationError(
                "Phone number must contain only digits and optionally '+', '-', '(', ')', or spaces."
            )
        return value

    def validate_customer_number(self, value):
        """Ensure customer_number is a positive integer within acceptable range."""
        if value <= 0:
            raise serializers.ValidationError("Customer number must be at least 1.")
        if value > 100:
            raise serializers.ValidationError("Customer number cannot exceed 100.")
        return value

    def validate_reservation_date(self, value):
        """Ensure reservation_date is in the future for new reservations."""
        from django.utils import timezone

        if value < timezone.now():
            raise serializers.ValidationError("Reservation date cannot be in the past.")
        return value


# ===========================
# Response Serializers
# ===========================


class BaseSingleReservationResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing a single reservation."""

    data = ReservationSerializer(
        help_text="Reservation details", required=True, many=False
    )

    class Meta:
        abstract = True


class BaseReservationListResponseSerializer(SuccessResponseSerializer):
    """Base serializer for responses containing multiple reservations."""

    data = ReservationSerializer(
        help_text="List of reservations", required=True, many=True
    )

    class Meta:
        abstract = True


class CreateReservationResponseSerializer(
    CreatedResponseSerializer, BaseSingleReservationResponseSerializer
):
    """
    Response serializer for reservation creation (201 Created).

    Example:
        {
            "data": {
                "id": 1,
                "name": "John Smith",
                "phone_number": "+1-800-555-0123",
                "customer_number": 4,
                "email": "john.smith@example.com",
                "table": 1,
                "reservation_date": "2024-03-15T19:00:00Z",
                "status": "PENDING",
                "status_display": "Pending",
                "created_at": "2024-03-06T12:00:00Z",
                "cancelled_at": null
            },
            "timestamp": "2024-03-06T12:00:00Z",
            "success": true,
            "status_code": 201,
            "message": "Reservation successfully created",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="Reservation successfully created",
    )

    class Meta:
        ref_name = "CreateReservationResponse"


class UpdateReservationResponseSerializer(BaseSingleReservationResponseSerializer):
    """
    Response serializer for reservation update (200 OK).

    Example:
        {
            "data": { ... },
            "timestamp": "2024-03-06T13:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Reservation successfully updated",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="Reservation successfully updated",
    )

    class Meta:
        ref_name = "UpdateReservationResponse"


class RetrieveReservationResponseSerializer(BaseSingleReservationResponseSerializer):
    """
    Response serializer for single reservation retrieval (200 OK).

    Example:
        {
            "data": { ... },
            "timestamp": "2024-03-06T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Reservation successfully retrieved",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="Reservation successfully retrieved",
    )

    class Meta:
        ref_name = "RetrieveReservationResponse"


class ListReservationResponseSerializer(BaseReservationListResponseSerializer):
    """
    Response serializer for multiple reservations retrieval (200 OK).

    Example:
        {
            "data": [ ... ],
            "timestamp": "2024-03-06T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Reservations successfully retrieved",
            "metadata": {}
        }
    """

    message = serializers.CharField(
        help_text="Success message",
        default="Reservations successfully retrieved",
    )

    class Meta:
        ref_name = "ListReservationResponse"


class PaginatedReservationResponseSerializer(PaginatedResponseSerializer):
    """
    Response serializer for paginated reservation list (200 OK).

    Example:
        {
            "data": [ ... ],
            "timestamp": "2024-03-06T12:00:00Z",
            "success": true,
            "status_code": 200,
            "message": "Reservations successfully retrieved",
            "metadata": {
                "pagination": {
                    "page": 1,
                    "page_size": 20,
                    "total_count": 100,
                    "total_pages": 5,
                    "has_next": true,
                    "has_previous": false
                }
            }
        }
    """

    data = ReservationSerializer(
        help_text="Paginated list of reservations", required=True, many=True
    )

    message = serializers.CharField(
        help_text="Success message",
        default="Reservations successfully retrieved",
    )

    class Meta:
        ref_name = "PaginatedReservationResponse"
