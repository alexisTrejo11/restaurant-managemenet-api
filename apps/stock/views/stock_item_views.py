from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.shared.response import ResponseWrapper
from ..models import StockItem
from ..services.stock_item_service import StockItemService
from ..serializers import StockItemSerializer
from ..documentation.stock_item_doc_data import (
    StockItemDocumentationData as stockItemDocData,
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class StockItemViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing stock item instances.
    """

    permission_classes = [IsAuthenticated]
    response_wrapper = ResponseWrapper
    serializer_class = StockItemSerializer
    queryset = StockItem.objects.all()

    @swagger_auto_schema(
        operation_id="list_stock_items",
        operation_summary=stockItemDocData.list_operation_summary,
        operation_description=stockItemDocData.list_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by category",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "supplier",
                openapi.IN_QUERY,
                description="Filter by supplier name",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            status.HTTP_200_OK: stockItemDocData.list_response,
            status.HTTP_401_UNAUTHORIZED: stockItemDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: stockItemDocData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: stockItemDocData.server_error_reponse,
        },
        tags=["Inventory"],
    )
    def list(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting stock item list.")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        logger.info(f"Returning {len(queryset)} items.")
        return ResponseWrapper.found(
            data=serializer.data,
            entity="Stock List",
        )

    @swagger_auto_schema(
        operation_id="retrieve_stock_item",
        operation_summary=stockItemDocData.retrieve_operation_summary,
        operation_description=stockItemDocData.retrieve_operation_description,
        responses={
            status.HTTP_200_OK: stockItemDocData.success_response,
            status.HTTP_404_NOT_FOUND: stockItemDocData.not_found_response,
            status.HTTP_401_UNAUTHORIZED: stockItemDocData.unauthorized_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: stockItemDocData.server_error_reponse,
        },
        tags=["Inventory"],
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is requesting details for stock item ID: {instance.id}."
        )

        serializer = self.get_serializer(instance)

        logger.info(f"Returning details for stock item ID: {instance.id}.")
        return ResponseWrapper.found(
            data=serializer.data,
            entity=f"Stock Item {instance.id}",
        )

    @swagger_auto_schema(
        operation_id="create_stock_item",
        operation_summary=stockItemDocData.create_operation_summary,
        operation_description=stockItemDocData.create_operation_description,
        request_body=StockItemSerializer,
        responses={
            status.HTTP_201_CREATED: stockItemDocData.success_response,
            status.HTTP_400_BAD_REQUEST: stockItemDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: stockItemDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: stockItemDocData.forbidden_reponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: stockItemDocData.server_error_reponse,
        },
        tags=["Inventory"],
    )
    def create(self, request, *args, **kwargs):
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is attempting to create a new stock item with data: {request.data}."
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_stock_item = StockItemService.create_stock_item(
            serializer.validated_data
        )

        logger.info(
            f"Stock Item ID: {created_stock_item.id} created successfully by user {user_id}."
        )
        return ResponseWrapper.created(
            data=self.get_serializer(created_stock_item).data,
            entity=f"Stock Item {created_stock_item.id}",
        )

    @swagger_auto_schema(
        operation_id="update_stock_item",
        operation_summary=stockItemDocData.update_operation_summary,
        operation_description=stockItemDocData.update_operation_description,
        request_body=StockItemSerializer,
        responses={
            status.HTTP_200_OK: stockItemDocData.success_response,
            status.HTTP_400_BAD_REQUEST: stockItemDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: stockItemDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: stockItemDocData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: stockItemDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: stockItemDocData.server_error_reponse,
        },
        tags=["Inventory"],
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is attempting to update stock_item ID: {instance.id} with data: {request.data}."
        )

        serializer = self.get_serializer(
            instance, data=request.data, partial=partial, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        updated_stock_item = StockItemService.update_stock_item(
            serializer.validated_data, instance
        )

        logger.info(
            f"Stock Item ID: {updated_stock_item.id} updated successfully by user {user_id}."
        )
        return ResponseWrapper.updated(
            data=self.get_serializer(updated_stock_item).data,
            entity=f"Stock Item {updated_stock_item.id}",
        )

    @swagger_auto_schema(
        operation_id="delete_stock_item",
        operation_summary=stockItemDocData.destroy_operation_summary,
        operation_description=stockItemDocData.destroy_operation_description,
        responses={
            status.HTTP_204_NO_CONTENT: "Stock item deleted successfully",
            status.HTTP_401_UNAUTHORIZED: stockItemDocData.unauthorized_reponse,
            status.HTTP_403_FORBIDDEN: stockItemDocData.forbidden_reponse,
            status.HTTP_404_NOT_FOUND: stockItemDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: stockItemDocData.server_error_reponse,
        },
        tags=["Inventory"],
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is attempting to delete stock_item ID: {instance.id}."
        )

        stock_item_id = instance.id
        StockItemService.delete_stock_item(instance)

        logger.info(
            f"Stock Item ID: {stock_item_id} deleted successfully by user {user_id}."
        )
        return ResponseWrapper.deleted(
            entity=f"Stock Item {stock_item_id}",
        )
