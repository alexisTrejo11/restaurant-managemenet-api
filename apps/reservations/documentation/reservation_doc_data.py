from ..serializers import ReservationSerializer
from drf_yasg import openapi
from apps.shared.open_api.error_response_schema import (
    NotFoundErrorResponseSerializer,
    ValidationErrorResponseSerializer,
    ErrorResponses,
)


# TODO: reutilize response
class ReservationAdminDocumentationData:
    """
    Documentation data for ReservationAdminViewSet endpoints
    """

    reservation_response = openapi.Response(
        description="Reservation response",
        schema=ReservationSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "customer": 101,
                    "table": 5,
                    "reservation_date": "2023-12-25",
                    "reservation_time": "19:00",
                    "party_size": 4,
                    "special_requests": "Window seat preferred",
                    "status": "confirmed",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                },
            }
        },
    )

    list_response = openapi.Response(
        description="List of all reservations",
        schema=ReservationSerializer(many=True),
        examples={
            "application/json": {
                "success": True,
                "message": "Found 3 reservations",
                "data": [
                    {
                        "id": 1,
                        "customer": 101,
                        "table": 5,
                        "reservation_date": "2023-12-25",
                        "party_size": 4,
                        "status": "confirmed",
                    },
                    {
                        "id": 2,
                        "customer": 102,
                        "table": 3,
                        "reservation_date": "2023-12-26",
                        "party_size": 2,
                        "status": "pending",
                    },
                ],
            }
        },
    )

    not_found_response = openapi.Response(
        description="Reservation not found",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Reservation not found",
                "errors": {"detail": "Reservation with ID 999 does not exist."},
            }
        },
    )

    validation_error_response = openapi.Response(
        description="Validation error",
        schema=ValidationErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Validation Error",
                "errors": {
                    "reservation_date": ["Date cannot be in the past."],
                    "party_size": ["Party size exceeds table capacity."],
                },
            }
        },
    )

    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    list_operation_summary = "List all reservations"
    list_operation_description = """
    Returns a list of all reservations in the system.
    
    **Permissions:**
    - Admin access required
    
    **Filtering:**
    - Filter by date: `?date=2023-12-25`
    - Filter by status: `?status=confirmed`
    - Filter by customer: `?customer_id=101`
    """

    retrieve_operation_summary = "Retrieve a reservation"
    retrieve_operation_description = """
    Returns detailed information about a specific reservation.
    
    **Permissions:**
    - Admin access required
    """

    create_operation_summary = "Create a reservation (Admin)"
    create_operation_description = """
    Creates a new reservation with admin privileges.
    
    **Permissions:**
    - Admin access required
    
    **Required Fields:**
    - `customer`: Customer ID
    - `table`: Table ID
    - `reservation_date`: Date in YYYY-MM-DD format
    - `reservation_time`: Time in HH:MM format
    - `party_size`: Number of guests
    """

    update_operation_summary = "Update a reservation (Admin)"
    update_operation_description = """
    Updates an existing reservation with admin privileges.
    
    **Permissions:**
    - Admin access required
    
    **Note:**
    - Can override any validation rules
    - Supports full updates only (PUT)
    """

    destroy_operation_summary = "Delete a reservation (Admin)"
    destroy_operation_description = """
    Deletes a reservation from the system.
    
    **Permissions:**
    - Admin access required
    
    **Note:**
    - This action is irreversible
    - Will send cancellation notification if reservation was confirmed
    """


class ReservationDocumentationData:
    """
    Documentation data for Reservation endpoints
    """

    # Common responses
    reservation_response = openapi.Response(
        description="Reservation response",
        schema=ReservationSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Reservation Requested. To confirm your reservation, please check your email.",
                "data": {
                    "id": 1,
                    "customer": 101,
                    "table": 5,
                    "reservation_date": "2023-12-25",
                    "reservation_time": "19:00",
                    "party_size": 4,
                    "special_requests": "Window seat preferred",
                    "status": "pending",
                    "created_at": "2023-01-01T12:00:00Z",
                },
            }
        },
    )

    today_reservations_response = openapi.Response(
        description="Today's reservations",
        schema=ReservationSerializer(many=True),
        examples={
            "application/json": {
                "success": True,
                "message": "Today's reservations retrieved successfully.",
                "data": [
                    {
                        "id": 1,
                        "customer": 101,
                        "table": 5,
                        "reservation_time": "19:00",
                        "party_size": 4,
                        "status": "confirmed",
                    },
                    {
                        "id": 2,
                        "customer": 102,
                        "table": 3,
                        "reservation_time": "20:00",
                        "party_size": 2,
                        "status": "confirmed",
                    },
                ],
            }
        },
    )

    status_update_response = openapi.Response(
        description="Status update response",
        examples={
            "application/json": {
                "success": True,
                "message": "Reservation Successfully Set As CONFIRMED",
                "data": None,
            }
        },
    )

    validation_error_response = openapi.Response(
        description="Validation error",
        schema=ValidationErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Validation Error",
                "errors": {
                    "reservation_date": ["Date cannot be in the past."],
                    "party_size": ["Party size exceeds table capacity."],
                },
            }
        },
    )

    invalid_status_response = openapi.Response(
        description="Invalid status response",
        examples={
            "application/json": {
                "success": False,
                "message": "Invalid status",
                "errors": {
                    "status": ["Valid statuses are: PENDING, CONFIRMED, CANCELLED"]
                },
            }
        },
    )

    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    create_operation_summary = "Request a new reservation"
    create_operation_description = """
    Creates a new reservation request.
    
    **Permissions:**
    - `AllowAny`: No authentication required
    
    **Required Fields:**
    - `customer`: Customer ID (if authenticated) or contact info
    - `table`: Table ID
    - `reservation_date`: Date in YYYY-MM-DD format
    - `reservation_time`: Time in HH:MM format
    - `party_size`: Number of guests
    
    **Note:**
    - Will send confirmation email
    - Initial status will be PENDING
    """

    today_operation_summary = "Get today's reservations"
    today_operation_description = """
    Returns all reservations scheduled for today.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Note:**
    - Only returns reservations for the authenticated user
    - Includes reservations from now until end of day
    """

    update_status_operation_summary = "Update reservation status"
    update_status_operation_description = """
    Updates the status of an existing reservation.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Valid Status Values:**
    - PENDING
    - CONFIRMED
    - CANCELLED
    
    **Note:**
    - Only the reservation owner or admin can update status
    - Status changes may trigger notifications
    """
