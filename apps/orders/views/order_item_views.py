from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import logging

from ..serializers import OrderItemSerializer
from ..services import OrderService, OrderItemService
from ..documentation.order_item_doc_data import OrderItemDocumentationData

from apps.shared.response import ResponseWrapper

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method="post",
    operation_id=OrderItemDocumentationData.add_items_operation_id,
    operation_summary=OrderItemDocumentationData.add_items_operation_summary,
    operation_description=OrderItemDocumentationData.add_items_operation_description,
    request_body=OrderItemSerializer(many=True),
    responses={
        status.HTTP_201_CREATED: OrderItemDocumentationData.order_items_list_response,
        status.HTTP_400_BAD_REQUEST: OrderItemDocumentationData.add_items_validation_error_response,
        status.HTTP_401_UNAUTHORIZED: OrderItemDocumentationData.unauthorized_response,
        status.HTTP_404_NOT_FOUND: OrderItemDocumentationData.order_not_found_response,
        status.HTTP_500_INTERNAL_SERVER_ERROR: OrderItemDocumentationData.server_error_response,
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
        return ResponseWrapper.bad_request(message="Order ID is required")

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

    return ResponseWrapper.created(
        data=OrderItemSerializer(updated_order.order_items.all(), many=True).data,
        entity=f"Order {order_id} Items",
    )


@swagger_auto_schema(
    method="post",
    operation_id=OrderItemDocumentationData.delete_items_operation_id,
    operation_summary=OrderItemDocumentationData.delete_items_operation_summary,
    operation_description=OrderItemDocumentationData.delete_items_operation_description,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "order_item_ids": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_INTEGER),
                description="List of order item IDs to delete",
            )
        },
        required=["order_item_ids"],
    ),
    responses={
        status.HTTP_200_OK: OrderItemDocumentationData.success_no_data_response,
        status.HTTP_400_BAD_REQUEST: OrderItemDocumentationData.delete_items_validation_error_response,
        status.HTTP_401_UNAUTHORIZED: OrderItemDocumentationData.unauthorized_response,
        status.HTTP_404_NOT_FOUND: OrderItemDocumentationData.order_or_items_not_found_response,
        status.HTTP_500_INTERNAL_SERVER_ERROR: OrderItemDocumentationData.server_error_response,
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
        return ResponseWrapper.bad_request(
            message="Both Order ID and Order Item IDs are required"
        )

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

    return ResponseWrapper.deleted(entity=f"Order Items {order_items_ids}")


# @permission_classes([permissions.IsAuthenticated])
@api_view(["PATCH"])
def set_items_as_delivered(request, order_id):
    order_items_ids = request.data.get("order_item_ids", [])

    if not order_id or not order_items_ids:
        return ResponseWrapper.bad_request(
            message="Both Order ID and Order Item IDs are required"
        )

    order = OrderService.get_order(order_id, active=True)
    OrderItemService.set_item_as_delivered(order, order_items_ids)

    return ResponseWrapper.success(
        message=f"Requested Items for Order {order_id} successfully marked as delivered"
    )
