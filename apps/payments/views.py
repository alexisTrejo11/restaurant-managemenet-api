import logging

from rest_framework import viewsets, status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.shared.response import ResponseWrapper
from apps.shared.pagination import CustomPagination

from .services.payment_service import PaymentService
from .serializers import PaymentSerializer
from .models import Payment
from .documentation.payment_doc_data import PaymentDocumentationData as PaymentDocData

logger = logging.getLogger(__name__)


class PaymentAdminViews(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    pagination_class = CustomPagination

    @swagger_auto_schema(
        operation_id="list_payments",
        operation_summary=PaymentDocData.list_operation_summary,
        operation_description=PaymentDocData.list_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by payment status",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "payment_method",
                openapi.IN_QUERY,
                description="Filter by payment method",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "start_date",
                openapi.IN_QUERY,
                description="Start date for date range filter (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "end_date",
                openapi.IN_QUERY,
                description="End date for date range filter (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "min_amount",
                openapi.IN_QUERY,
                description="Minimum payment amount",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "max_amount",
                openapi.IN_QUERY,
                description="Maximum payment amount",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of results per page",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            status.HTTP_200_OK: PaymentDocData.payment_list_response,
            status.HTTP_401_UNAUTHORIZED: PaymentDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: PaymentDocData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: PaymentDocData.server_error_reponse,
        },
        tags=["Payments (Admin)"],
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
        return ResponseWrapper.found(
            data=serializer.data,
            entity="Payment List",
            metadata={
                "pagination": self.paginator.get_paginated_response({}).data,
                "applied_filters": applied_filters,
            },
        )

    @swagger_auto_schema(
        operation_id="retrieve_payment",
        operation_summary=PaymentDocData.retrieve_operation_summary,
        operation_description=PaymentDocData.retrieve_operation_description,
        responses={
            status.HTTP_200_OK: PaymentDocData.payment_response,
            status.HTTP_401_UNAUTHORIZED: PaymentDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: PaymentDocData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: PaymentDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: PaymentDocData.server_error_reponse,
        },
        tags=["Payments (Admin)"],
    )
    def retrieve(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        instance = self.get_object()
        logger.info(
            f"User {user_id} is requesting details for payment ID: {instance.id}."
        )

        serializer = self.get_serializer(instance)
        logger.info(f"Returning details for table ID: {instance.id}.")
        return ResponseWrapper.found(
            data=serializer.data, entity=f"Payment {instance.id}"
        )

    @swagger_auto_schema(
        operation_id="create_payment",
        operation_summary=PaymentDocData.create_operation_summary,
        operation_description=PaymentDocData.create_operation_description,
        request_body=PaymentSerializer,
        responses={
            status.HTTP_201_CREATED: PaymentDocData.payment_response,
            status.HTTP_400_BAD_REQUEST: PaymentDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: PaymentDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: PaymentDocData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: PaymentDocData.server_error_reponse,
        },
        tags=["Payments (Admin)"],
    )
    def create(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting to create a Payment.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PaymentService.create_payment(serializer.validated_data)
        logger.info(f"Payment ID: {payment.id} created successfully.")

        serializer = self.get_serializer(payment)
        return ResponseWrapper.created(data=serializer.data, entity="Payment")

    @swagger_auto_schema(
        operation_id="update_payment",
        operation_summary=PaymentDocData.update_operation_summary,
        operation_description=PaymentDocData.update_operation_description,
        request_body=PaymentSerializer,
        responses={
            status.HTTP_200_OK: PaymentDocData.payment_response,
            status.HTTP_400_BAD_REQUEST: PaymentDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: PaymentDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: PaymentDocData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: PaymentDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: PaymentDocData.server_error_reponse,
        },
        tags=["Payments (Admin)"],
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
        return ResponseWrapper.created(
            data=serializer.data,
            entity=f"Payment {payment.id}",
        )

    @swagger_auto_schema(
        operation_id="delete_payment",
        operation_summary=PaymentDocData.destroy_operation_summary,
        operation_description=PaymentDocData.destroy_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "hard_delete",
                openapi.IN_QUERY,
                description="Permanently delete record if true",
                type=openapi.TYPE_BOOLEAN,
            )
        ],
        responses={
            status.HTTP_204_NO_CONTENT: PaymentDocData.success_no_data,
            status.HTTP_401_UNAUTHORIZED: PaymentDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: PaymentDocData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: PaymentDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: PaymentDocData.server_error_reponse,
        },
        tags=["Payments (Admin)"],
    )
    def destroy(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        instance = self.get_object()
        payment_id = instance.id
        is_hard_delete = self.request.query_params.get("hard_delete", False)

        logger.info(f"User {user_id} is requesting to delete Payment Id {payment_id}.")
        PaymentService.delete_payment(instance, hard_delete=is_hard_delete)

        return ResponseWrapper.deleted(f"Payment {payment_id}")

    def get_queryset(self):
        """Apply search filters to the base queryset"""
        queryset = Payment.objects.all()
        query_params = self.request.query_params
        search_params = PaymentService.get_search_params(query_params)
        return Payment.objects.dynamic_search(search_params)
