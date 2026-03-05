from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Reservation
from ..serializers import ReservationSerializer
from ..services.reservation_service import ReservationService
from ..documentation.reservation_doc_data import (
    ReservationAdminDocumentationData as ReservationDocData,
)

from apps.shared.response import ResponseWrapper

import logging

logger = logging.getLogger(__name__)


# TODO: Add Filters
class ReservationAdminViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        operation_id="list_reservations_admin",
        operation_summary=ReservationDocData.list_operation_summary,
        operation_description=ReservationDocData.list_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "date",
                openapi.IN_QUERY,
                description="Filter by reservation date (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by status (pending/confirmed/cancelled)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "customer_id",
                openapi.IN_QUERY,
                description="Filter by customer ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            status.HTTP_200_OK: ReservationDocData.list_response,
            status.HTTP_401_UNAUTHORIZED: ReservationDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: ReservationDocData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ReservationDocData.server_error_reponse,
        },
        tags=["Reservations (Admin)"],
    )
    def list(self, request):
        queryset = Reservation.objects.all()
        serializer = ReservationSerializer(queryset, many=True)
        return ResponseWrapper.found(
            data=serializer.data,
            entity="Reservation List",
        )

    @swagger_auto_schema(
        operation_id="retrieve_reservation_admin",
        operation_summary=ReservationDocData.retrieve_operation_summary,
        operation_description=ReservationDocData.retrieve_operation_description,
        responses={
            status.HTTP_200_OK: ReservationDocData.reservation_response,
            status.HTTP_404_NOT_FOUND: ReservationDocData.not_found_response,
            status.HTTP_401_UNAUTHORIZED: ReservationDocData.unauthorized_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ReservationDocData.server_error_reponse,
        },
        tags=["Reservations (Admin)"],
    )
    def retrieve(self, request, pk=None):
        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=pk)

        serializer = ReservationSerializer(reservation)

        return ResponseWrapper.found(
            entity=f"Reservation {pk}",
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_id="create_reservation_admin",
        operation_summary=ReservationDocData.create_operation_summary,
        operation_description=ReservationDocData.create_operation_description,
        request_body=ReservationSerializer,
        responses={
            status.HTTP_201_CREATED: ReservationDocData.reservation_response,
            status.HTTP_400_BAD_REQUEST: ReservationDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: ReservationDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: ReservationDocData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ReservationDocData.server_error_reponse,
        },
        tags=["Reservations (Admin)"],
    )
    def create(self, request):
        serializer = ReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reservation_created = ReservationService.create_reservation(
            serializer.validated_data, is_admin=True
        )

        return ResponseWrapper.created(
            data=ReservationSerializer(reservation_created).data, entity="Reservation"
        )

    @swagger_auto_schema(
        operation_id="update_reservation_admin",
        operation_summary=ReservationDocData.update_operation_summary,
        operation_description=ReservationDocData.update_operation_description,
        request_body=ReservationSerializer,
        responses={
            status.HTTP_200_OK: ReservationDocData.reservation_response,
            status.HTTP_400_BAD_REQUEST: ReservationDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: ReservationDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: ReservationDocData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: ReservationDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ReservationDocData.server_error_reponse,
        },
        tags=["Reservations (Admin)"],
    )
    def update(self, request, pk=None):
        queryset = Reservation.objects.all()
        existing_reservation = get_object_or_404(queryset, pk=pk)

        serializer = ReservationSerializer(
            existing_reservation, data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)

        reservation_updated = serializer.save()
        return ResponseWrapper.updated(
            data=ReservationSerializer(reservation_updated).data,
            entity=f"Reservation {pk}",
        )

    @swagger_auto_schema(
        operation_id="delete_reservation_admin",
        operation_summary=ReservationDocData.destroy_operation_summary,
        operation_description=ReservationDocData.destroy_operation_description,
        responses={
            status.HTTP_204_NO_CONTENT: "Reservation deleted successfully",
            status.HTTP_401_UNAUTHORIZED: ReservationDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: ReservationDocData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: ReservationDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ReservationDocData.server_error_reponse,
        },
        tags=["Reservations (Admin)"],
    )
    def destroy(self, request, pk=None):
        queryset = Reservation.objects.all()
        reservation = get_object_or_404(queryset, pk=pk)
        reservation.delete()
        return ResponseWrapper.deleted(f"Reservation {pk}")
