import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..models import Reservation
from ..serializers import (
    ReservationSerializer,
    CreateReservationResponseSerializer,
    UpdateReservationResponseSerializer,
    RetrieveReservationResponseSerializer,
    ListReservationResponseSerializer,
    PaginatedReservationResponseSerializer,
)
from ..services.reservation_service import ReservationService
from apps.shared.response import (
    NoContentResponseSerializer,
    ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
    UnauthorizedErrorResponseSerializer,
    ForbiddenErrorResponseSerializer,
    ServerErrorResponseSerializer,
)

logger = logging.getLogger(__name__)

COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: UnauthorizedErrorResponseSerializer,
    status.HTTP_403_FORBIDDEN: ForbiddenErrorResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ServerErrorResponseSerializer,
}


@extend_schema(tags=["Reservations (Admin)"])
class ReservationAdminViewSet(viewsets.ViewSet):
    """
    ViewSet for admin management of reservations.

    Provides full CRUD operations with filtering capabilities.
    Admin-only access.
    """

    @extend_schema(
        operation_id="list_reservations_admin",
        summary="List all reservations",
        description="Retrieves a paginated list of all reservations with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by reservation date (YYYY-MM-DD)",
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by status (PENDING, BOOKED, ATTENDED, NOT_ATTENDED, CANCELLED)",
                required=False,
            ),
            OpenApiParameter(
                name="customer_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by customer ID",
                required=False,
            ),
        ],
        responses={
            200: PaginatedReservationResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def list(self, request):
        """List all reservations with optional filtering."""
        queryset = Reservation.objects.all()
        serializer = ReservationSerializer(queryset, many=True)
        response_data = PaginatedReservationResponseSerializer(serializer.data).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_reservation_admin",
        summary="Get reservation details",
        description="Retrieves detailed information for a specific reservation.",
        responses={
            200: RetrieveReservationResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def retrieve(self, request, pk=None):
        """Retrieve a specific reservation."""
        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=pk)
        serializer = ReservationSerializer(reservation)
        response_data = RetrieveReservationResponseSerializer(serializer.data).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_reservation_admin",
        summary="Create new reservation",
        description="Admin endpoint to create a new reservation.",
        request=ReservationSerializer,
        responses={
            201: CreateReservationResponseSerializer,
            400: ValidationErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def create(self, request):
        """Create a new reservation."""
        serializer = ReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation_created = ReservationService.create_reservation(
            serializer.validated_data, is_admin=True
        )

        response_data = CreateReservationResponseSerializer(
            ReservationSerializer(reservation_created).data
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_reservation_admin",
        summary="Update reservation",
        description="Updates an existing reservation. Supports partial updates.",
        request=ReservationSerializer,
        responses={
            200: UpdateReservationResponseSerializer,
            400: ValidationErrorResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def update(self, request, pk=None):
        """Update an existing reservation (full or partial)."""
        queryset = Reservation.objects.all()
        existing_reservation = get_object_or_404(queryset, pk=pk)

        serializer = ReservationSerializer(
            existing_reservation, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)

        reservation_updated = serializer.save()
        response_data = UpdateReservationResponseSerializer(
            ReservationSerializer(reservation_updated).data
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_reservation_admin",
        summary="Delete reservation",
        description="Permanently removes a reservation from the system.",
        responses={
            204: NoContentResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, pk=None):
        """Delete a reservation."""
        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=pk)
        reservation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
