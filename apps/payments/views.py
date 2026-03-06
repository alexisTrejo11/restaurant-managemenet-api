import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.shared.pagination import CustomPagination
from apps.shared.response.serializers import (
    ApiResponseSerializer,
    NoContentResponseSerializer,
)
from .services.payment_service import PaymentService
from .serializers import (
    PaymentSerializer,
    CreatePaymentResponseSerializer,
    UpdatePaymentResponseSerializer,
    RetrievePaymentResponseSerializer,
    ListPaymentResponseSerializer,
    PaginatedPaymentsResponseSerializer,
)
from .models import Payment

logger = logging.getLogger(__name__)

# Global error response mapping to reduce verbosity
COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: ApiResponseSerializer,
    status.HTTP_403_FORBIDDEN: ApiResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ApiResponseSerializer,
}


@extend_schema(tags=["Payments (Admin)"])
class PaymentAdminViews(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination

    @extend_schema(
        operation_id="list_payments",
        summary="List all payments",
        description="Retrieve a paginated list of payments with optional filtering by status, method, date range, and amount",
        parameters=[
            OpenApiParameter(
                "status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by payment status (PENDING, COMPLETED, REFUNDED, CANCELLED)",
                required=False,
            ),
            OpenApiParameter(
                "payment_method",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by payment method (CASH, CARD, TRANSACTION)",
                required=False,
            ),
            OpenApiParameter(
                "start_date",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Start date for date range filter (YYYY-MM-DD format)",
                required=False,
            ),
            OpenApiParameter(
                "end_date",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="End date for date range filter (YYYY-MM-DD format)",
                required=False,
            ),
            OpenApiParameter(
                "min_amount",
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description="Minimum payment amount filter",
                required=False,
            ),
            OpenApiParameter(
                "max_amount",
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
                description="Maximum payment amount filter",
                required=False,
            ),
            OpenApiParameter(
                "page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of results per page",
                required=False,
            ),
        ],
        responses={
            200: PaginatedPaymentsResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def list(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting payment list.")

        query_params = self.request.query_params
        search_params = PaymentService.get_search_params(query_params)
        applied_filters = PaymentService.get_applied_filter_names(search_params)

        queryset = Payment.objects.dynamic_search(search_params)
        page = self.paginate_queryset(queryset)

        logger.info(
            f"Returning {len(page if page else [])} payments with applied filters: {applied_filters}"
        )

        serializer = self.get_serializer(page, many=True)
        response_data = PaginatedPaymentsResponseSerializer(
            {
                "data": serializer.data,
                "message": "Payments retrieved successfully",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_payment",
        summary="Retrieve a single payment",
        description="Get detailed information about a specific payment by ID",
        responses={
            200: RetrievePaymentResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        instance = self.get_object()
        logger.info(
            f"User {user_id} is requesting details for payment ID: {instance.id}."
        )

        serializer = self.get_serializer(instance)
        logger.info(f"Returning details for payment ID: {instance.id}.")
        response_data = RetrievePaymentResponseSerializer(
            {
                "data": serializer.data,
                "message": "Payment retrieved successfully",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_payment",
        summary="Create a new payment",
        description="Create a new payment record for an order or standalone",
        request=PaymentSerializer,
        responses={
            201: CreatePaymentResponseSerializer,
            400: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def create(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting to create a Payment.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PaymentService.create_payment(serializer.validated_data)
        logger.info(f"Payment ID: {payment.id} created successfully.")

        serializer = self.get_serializer(payment)
        response_data = CreatePaymentResponseSerializer(
            {
                "data": serializer.data,
                "message": f"Payment {payment.id} successfully created",
            }
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_payment",
        summary="Update a payment",
        description="Update payment information (method, status, discount, VAT, etc.)",
        request=PaymentSerializer,
        responses={
            200: UpdatePaymentResponseSerializer,
            400: ApiResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def update(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        instance = self.get_object()
        logger.info(f"User {user_id} is requesting to update Payment Id {instance.id}.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PaymentService.update_payment(instance, serializer.validated_data)
        logger.info(f"Payment ID: {payment.id} updated successfully.")

        serializer = self.get_serializer(payment)
        response_data = UpdatePaymentResponseSerializer(
            {
                "data": serializer.data,
                "message": f"Payment {payment.id} successfully updated",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_payment",
        summary="Delete a payment",
        description="Remove or soft-delete a payment record",
        parameters=[
            OpenApiParameter(
                "hard_delete",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Permanently delete payment record if true (default: soft delete)",
                required=False,
            )
        ],
        responses={
            204: NoContentResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        instance = self.get_object()
        payment_id = instance.id
        is_hard_delete = self.request.query_params.get("hard_delete", False)

        logger.info(f"User {user_id} is requesting to delete Payment Id {payment_id}.")
        PaymentService.delete_payment(instance, hard_delete=is_hard_delete)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        """Apply search filters to the base queryset"""
        queryset = Payment.objects.all()
        query_params = self.request.query_params
        search_params = PaymentService.get_search_params(query_params)
        return Payment.objects.dynamic_search(search_params)
