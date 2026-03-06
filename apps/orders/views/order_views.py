import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..serializers import (
    OrderSerializer,
    CreateOrderResponseSerializer,
    UpdateOrderResponseSerializer,
    RetrieveOrderResponseSerializer,
    ListOrderResponseSerializer,
    PaginatedOrdersResponseSerializer,
)
from ..models import Order
from ..services.order_service import OrderService
from apps.payments.services.payment_service import PaymentService
from apps.payments.serializers import PaymentSerializer
from apps.shared.response.serializers import (
    ApiResponseSerializer,
    NoContentResponseSerializer,
)

logger = logging.getLogger(__name__)

# Global error response mapping to reduce verbosity
COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: ApiResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ApiResponseSerializer,
}


@extend_schema(tags=["Orders"])
class OrderViewsSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = []

    @extend_schema(
        operation_id="list_orders",
        summary="List all orders",
        description="Retrieve a paginated list of all orders with optional status and table filtering",
        parameters=[
            OpenApiParameter(
                "status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by order status (IN_PROGRESS, COMPLETED, or CANCELLED)",
                required=False,
            ),
            OpenApiParameter(
                "table_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by table ID",
                required=False,
            ),
        ],
        responses={
            200: PaginatedOrdersResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def list(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting order list.")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        logger.info(f"Returning {len(queryset)} orders.")
        response_data = ListOrderResponseSerializer(
            {
                "data": serializer.data,
                "message": "Orders retrieved successfully",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_order",
        summary="Retrieve a single order",
        description="Get detailed information about a specific order by ID",
        responses={
            200: RetrieveOrderResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting retrieving order {order.id}.")

        serializer = self.get_serializer(order)

        logger.info(f"Returning details for order ID: {order.id}.")
        response_data = RetrieveOrderResponseSerializer(
            {
                "data": serializer.data,
                "message": f"Order {order.id} retrieved successfully",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_order",
        summary="Create a new order",
        description="Create a new order for a specific table",
        request=OrderSerializer,
        responses={
            201: CreateOrderResponseSerializer,
            400: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def create(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting creating order.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.start_order(serializer.validated_data)

        logger.info(f"Order ID: {order.id} created successfully.")
        serializer = self.get_serializer(order)
        response_data = CreateOrderResponseSerializer(
            {
                "data": serializer.data,
                "message": f"Order {order.id} successfully created",
            }
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_order",
        summary="Update an order",
        description="Update order status or assigned table",
        parameters=[
            OpenApiParameter(
                "status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="New status for the order (IN_PROGRESS, COMPLETED, or CANCELLED)",
                required=False,
            ),
            OpenApiParameter(
                "table_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="New table ID for the order",
                required=False,
            ),
        ],
        responses={
            200: UpdateOrderResponseSerializer,
            400: ApiResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
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
        response_data = UpdateOrderResponseSerializer(
            {
                "data": serializer.data,
                "message": f"Order {order.id} successfully updated",
            }
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_order",
        summary="Delete an order",
        description="Remove an order from the system",
        responses={
            204: NoContentResponseSerializer,
            400: ApiResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        order_id = order.id
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting deleting order {order_id}.")

        OrderService.delete_order(order)

        logger.info(f"Order ID: {order_id} deleted successfully.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="complete_order",
        summary="Complete an order",
        description="Mark an order as completed and initiate payment",
        responses={
            200: ApiResponseSerializer,
            400: ApiResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
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
        response_data = {
            "data": payment_serializer.data,
            "message": f"Order {order.id} successfully completed. Payment {payment.id} initiated pending payment",
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="cancel_order",
        summary="Cancel an order",
        description="Mark an order as cancelled",
        responses={
            200: ApiResponseSerializer,
            400: ApiResponseSerializer,
            404: ApiResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    @action(detail=True, methods=["patch"])
    def cancel(self, request, *args, **kwargs):
        order = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting to cancel status order {order.id}.")

        OrderService.cancel_order(order)
        logger.info(f"Order ID: {order.id} successfully cancelled.")

        response_data = {
            "message": f"Order {order.id} successfully cancelled",
        }
        return Response(response_data, status=status.HTTP_200_OK)
