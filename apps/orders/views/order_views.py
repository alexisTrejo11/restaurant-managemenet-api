from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import logging

from ..documentation.order_doc_data import OrderDocumentationData
from ..serializers import OrderSerializer
from ..models import Order
from ..services.order_service import OrderService
from apps.payments.services.payment_service import PaymentService
from apps.payments.serializers import PaymentSerializer

from apps.shared.response import ResponseWrapper

logger = logging.getLogger(__name__)


class OrderViewsSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = []

    @swagger_auto_schema(
        operation_id="list_orders",
        operation_summary=OrderDocumentationData.list_operation_summary,
        operation_description=OrderDocumentationData.list_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by order status",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "table_id",
                openapi.IN_QUERY,
                description="Filter by table ID",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            status.HTTP_200_OK: OrderDocumentationData.order_list_response,
            status.HTTP_401_UNAUTHORIZED: OrderDocumentationData.unauthorized_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OrderDocumentationData.server_error_reponse,
        },
        tags=["Orders"],
    )
    def list(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting order list.")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        logger.info(f"Returning {len(queryset)} tables.")
        return ResponseWrapper.found(
            data=serializer.data,
            entity="Order List",
        )

    @swagger_auto_schema(
        operation_id="retrieve_order",
        operation_summary=OrderDocumentationData.retrieve_operation_summary,
        operation_description=OrderDocumentationData.retrieve_operation_description,
        responses={
            status.HTTP_200_OK: OrderDocumentationData.order_response,
            status.HTTP_401_UNAUTHORIZED: OrderDocumentationData.unauthorized_reponse,
            status.HTTP_404_NOT_FOUND: OrderDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OrderDocumentationData.server_error_reponse,
        },
        tags=["Orders"],
    )
    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting retrieving order {order.id}.")

        serializer = self.get_serializer(order)

        logger.info(f"Returning details for order ID: {order.id}.")
        return ResponseWrapper.found(
            data=serializer.data,
            entity=f"Order {order.id}",
        )

    @swagger_auto_schema(
        operation_id="create_order",
        operation_summary=OrderDocumentationData.create_operation_summary,
        operation_description=OrderDocumentationData.create_operation_description,
        request_body=OrderSerializer,
        responses={
            status.HTTP_201_CREATED: OrderDocumentationData.order_response,
            status.HTTP_400_BAD_REQUEST: OrderDocumentationData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: OrderDocumentationData.unauthorized_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OrderDocumentationData.server_error_reponse,
        },
        tags=["Orders"],
    )
    def create(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting creating order.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.start_order(serializer.validated_data)

        logger.info(f"Order ID: {order.id} created successfully.")
        serializer = self.get_serializer(order)
        return ResponseWrapper.created(
            data=serializer.data,
            entity=f"Order {order.id}",
        )

    @swagger_auto_schema(
        operation_id="update_order",
        operation_summary=OrderDocumentationData.update_operation_summary,
        operation_description=OrderDocumentationData.update_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="New status for the order",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "table_id",
                openapi.IN_QUERY,
                description="New table ID for the order",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            status.HTTP_200_OK: OrderDocumentationData.order_response,
            status.HTTP_400_BAD_REQUEST: OrderDocumentationData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: OrderDocumentationData.unauthorized_reponse,
            status.HTTP_404_NOT_FOUND: OrderDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OrderDocumentationData.server_error_reponse,
        },
        tags=["Orders"],
    )
    def update(self, request, *args, **kwargs):
        order = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting updating order {order.id}.")

        new_status = request.query_params.get("status")
        new_table = request.query_params.get("table_id")

        order_updated = OrderService.update_order(order, new_status, new_table)
        logger.info(f"Order ID: {order.id} updated successfully.")

        serializer = self.get_serializer(order_updated)
        return ResponseWrapper.updated(
            data=serializer.data,
            entity=f"Order {order.id}",
        )

    @swagger_auto_schema(
        operation_id="update_order",
        operation_summary=OrderDocumentationData.update_operation_summary,
        operation_description=OrderDocumentationData.update_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="New status for the order",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "table_id",
                openapi.IN_QUERY,
                description="New table ID for the order",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            status.HTTP_200_OK: OrderDocumentationData.order_response,
            status.HTTP_400_BAD_REQUEST: OrderDocumentationData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: OrderDocumentationData.unauthorized_reponse,
            status.HTTP_404_NOT_FOUND: OrderDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OrderDocumentationData.server_error_reponse,
        },
        tags=["Orders"],
    )
    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        order_id = order.id
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting deleting order {order_id}.")

        OrderService.delete_order(order)

        logger.info(f"Order ID: {order_id} deleted successfully.")
        return ResponseWrapper.deleted(
            entity=f"Order {order_id}",
        )

    @swagger_auto_schema(
        operation_id="complete_order",
        operation_summary=OrderDocumentationData.complete_operation_summary,
        operation_description=OrderDocumentationData.complete_operation_description,
        responses={
            status.HTTP_200_OK: OrderDocumentationData.order_response,
            status.HTTP_400_BAD_REQUEST: OrderDocumentationData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: OrderDocumentationData.unauthorized_reponse,
            status.HTTP_404_NOT_FOUND: OrderDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OrderDocumentationData.server_error_reponse,
        },
        tags=["Orders"],
    )
    @action(detail=True, methods=["patch"])
    def complete(self, request, *args, **kwargs):
        order = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is requesting to complete status order {order.id}."
        )

        order_completed = OrderService.complete_order(order)
        payment = PaymentService.create_payment_from_order(order_completed)

        payment_serializer = PaymentSerializer(payment)
        return ResponseWrapper.success(
            data=payment_serializer.data,
            message=f"Order {order.id} Succesfully Completed. A Payment with Id {payment.id} was inited pending to be paid",
        )

    @swagger_auto_schema(
        operation_id="cancel_order",
        operation_summary=OrderDocumentationData.cancel_operation_summary,
        operation_description=OrderDocumentationData.cancel_operation_description,
        responses={
            status.HTTP_200_OK: OrderDocumentationData.success_no_data,
            status.HTTP_400_BAD_REQUEST: OrderDocumentationData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: OrderDocumentationData.unauthorized_reponse,
            status.HTTP_404_NOT_FOUND: OrderDocumentationData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: OrderDocumentationData.server_error_reponse,
        },
        tags=["Orders"],
    )
    @action(detail=True, methods=["patch"])
    def cancel(self, request, *args, **kwargs):
        order = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting to cancel status order {order.id}.")

        OrderService.cancel_order(order)
        logger.info(f"Order ID: {order.id} Succesfully Cancelled.")

        return ResponseWrapper.success(
            message=f"Order {order.id} Succesfully Cancelled"
        )
