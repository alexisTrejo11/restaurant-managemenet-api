import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..serializers import (
    OrderItemSerializer,
    CreateOrderItemResponseSerializer,
    ListOrderItemResponseSerializer,
)
from ..services import OrderService, OrderItemService
from apps.shared.response.serializers import ApiResponseSerializer

logger = logging.getLogger(__name__)

# Global error response mapping to reduce verbosity
COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: ApiResponseSerializer,
    status.HTTP_404_NOT_FOUND: ApiResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ApiResponseSerializer,
}


@extend_schema(
    operation_id="add_order_items",
    summary="Add items to an order",
    description="Add one or more menu items to an existing order",
    request=OrderItemSerializer(many=True),
    responses={
        201: CreateOrderItemResponseSerializer,
        400: ApiResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Order Items"],
)
@permission_classes([permissions.IsAuthenticated])
@api_view(["POST"])
def add_order_item(request, order_id):
    """
    API endpoint to add items to an order
    """
    if not order_id:
        response_data = {
            "message": "Order ID is required",
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id if request.user.is_authenticated else "Anonymous"
    logger.info(
        f"User {user_id} adding items to order {order_id}", extra={"data": request.data}
    )

    order = OrderService.get_order(order_id)
    serializer = OrderItemSerializer(data=request.data, many=True)
    serializer.is_valid(raise_exception=True)

    updated_order = OrderItemService.add_items(order, serializer.validated_data)

    logger.info(
        f"Items added to order {order_id} by user {user_id}",
        extra={"item_count": len(serializer.validated_data)},
    )

    response_serializer = OrderItemSerializer(
        updated_order.order_items.all(), many=True
    )
    response_data = CreateOrderItemResponseSerializer(
        {
            "data": response_serializer.data,
            "message": f"Items successfully added to order {order_id}",
        }
    ).data
    return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(
    operation_id="delete_order_items",
    summary="Remove items from an order",
    description="Delete one or more items from an existing order",
    request={
        "type": "object",
        "properties": {
            "order_item_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of order item IDs to delete",
            }
        },
        "required": ["order_item_ids"],
    },
    responses={
        200: ApiResponseSerializer,
        400: ApiResponseSerializer,
        404: ApiResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Order Items"],
)
@permission_classes([permissions.IsAuthenticated])
@api_view(["POST"])
def delete_order_item(request, order_id):
    """
    API endpoint to delete items from an order
    """
    order_items_ids = request.data.get("order_item_ids", [])

    if not order_id or not order_items_ids:
        response_data = {
            "message": "Both Order ID and Order Item IDs are required",
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.user.id if request.user.is_authenticated else "Anonymous"
    logger.info(
        f"User {user_id} removing items from order {order_id}",
        extra={"item_ids": order_items_ids},
    )

    order = OrderService.get_order(order_id)
    OrderItemService.delete_items(order, order_items_ids)

    logger.info(
        f"Items removed from order {order_id} by user {user_id}",
        extra={"item_ids": order_items_ids},
    )

    response_data = {
        "message": f"Items {order_items_ids} successfully removed from order {order_id}",
    }
    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="mark_items_as_delivered",
    summary="Mark order items as delivered",
    description="Mark specified order items as delivered to the customer",
    request={
        "type": "object",
        "properties": {
            "order_item_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "List of order item IDs to mark as delivered",
            }
        },
        "required": ["order_item_ids"],
    },
    responses={
        200: ApiResponseSerializer,
        400: ApiResponseSerializer,
        404: ApiResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Order Items"],
)
@api_view(["PATCH"])
def set_items_as_delivered(request, order_id):
    order_items_ids = request.data.get("order_item_ids", [])

    if not order_id or not order_items_ids:
        response_data = {
            "message": "Both Order ID and Order Item IDs are required",
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    order = OrderService.get_order(order_id, active=True)
    OrderItemService.set_item_as_delivered(order, order_items_ids)

    response_data = {
        "message": f"Items {order_items_ids} for order {order_id} successfully marked as delivered",
    }
    return Response(response_data, status=status.HTTP_200_OK)
