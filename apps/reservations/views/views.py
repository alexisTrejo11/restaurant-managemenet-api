import logging
from datetime import timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..serializers import (
    ReservationSerializer,
    CreateReservationResponseSerializer,
    ListReservationResponseSerializer,
)
from ..services.reservation_service import ReservationService
from apps.shared.response import (
    ValidationErrorResponseSerializer,
    UnauthorizedErrorResponseSerializer,
    ServerErrorResponseSerializer,
)

logger = logging.getLogger(__name__)

COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: UnauthorizedErrorResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ServerErrorResponseSerializer,
}


@extend_schema(
    operation_id="request_reservation",
    summary="Request a new reservation",
    description="Allows customers to request a new table reservation. Requires valid customer details and available table.",
    request=ReservationSerializer,
    responses={
        201: CreateReservationResponseSerializer,
        400: ValidationErrorResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Reservations"],
)
@api_view(["POST"])
@permission_classes([AllowAny])
def request_user_reservation(request):
    """Request a new table reservation."""
    user_id = getattr(request.user, "id", "Anonymous")
    logger.info(
        f"User {user_id} is requesting to create a reservation with data: {request.data}"
    )

    serializer = ReservationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    reservation_created = ReservationService.create_reservation(
        validated_data=serializer.validated_data, is_admin=False
    )

    reservation_serialized = ReservationSerializer(reservation_created)
    logger.info(
        f"Reservation created successfully by user {user_id}. ID: {reservation_created.id}"
    )

    response_data = CreateReservationResponseSerializer(
        reservation_serialized.data
    ).data
    return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(
    operation_id="get_today_reservations",
    summary="Get today's reservations",
    description="Retrieves all reservations scheduled for today and tomorrow.",
    responses={
        200: ListReservationResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Reservations"],
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_today_reservations(request):
    """Get all reservations for today."""
    user = request.user
    user_id = user.id
    logger.info(f"User {user_id} is requesting today's reservations")

    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=2) - timedelta(microseconds=1)

    reservations = ReservationService.get_reservation_by_date_range(today, tomorrow)
    if len(reservations) == 0:
        response_data = ListReservationResponseSerializer(
            {"data": [], "message": "No reservations scheduled today"}
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    logger.info(f"User {user_id} retrieved {len(reservations)} reservations.")

    reservations_serialized = ReservationSerializer(reservations, many=True)
    response_data = ListReservationResponseSerializer(reservations_serialized.data).data
    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="update_reservation_status",
    summary="Update reservation status",
    description="Updates the status of an existing reservation (PENDING, BOOKED, ATTENDED, NOT_ATTENDED, CANCELLED).",
    parameters=[
        OpenApiParameter(
            name="reservation_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID of the reservation to update",
            required=True,
        ),
        OpenApiParameter(
            name="new_status",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="New status (PENDING/BOOKED/ATTENDED/NOT_ATTENDED/CANCELLED)",
            required=True,
        ),
    ],
    responses={
        200: ListReservationResponseSerializer,
        400: ValidationErrorResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Reservations"],
)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_status_reservation(request, reservation_id: int, new_status: str):
    """Update the status of a reservation."""
    user = request.user
    user_id = user.id
    new_status = new_status.upper()
    logger.info(
        f"User {user_id} is attempting to update reservation ID: {reservation_id} to status: {new_status}"
    )

    if not new_status:
        logger.warning(
            f"User {user_id} tried to update reservation {reservation_id} without providing a status."
        )
        return Response(
            {"error": "Status is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not ReservationService.is_status_valid(new_status):
        logger.warning(
            f"User {user_id} provided an invalid status: {new_status} for reservation {reservation_id}."
        )
        return Response(
            {"error": "Invalid status"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ReservationService.update_status_reservation(reservation_id, new_status)
    logger.info(
        f"Reservation {reservation_id} was successfully updated to status: {new_status} by user {user_id}."
    )

    return Response(
        {
            "success": True,
            "message": f"Reservation successfully set to {new_status}",
        },
        status=status.HTTP_200_OK,
    )
