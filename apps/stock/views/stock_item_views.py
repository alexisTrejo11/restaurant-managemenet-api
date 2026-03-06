import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..models import StockItem
from ..services.stock_item_service import StockItemService
from ..serializers import (
    StockItemSerializer,
    CreateStockItemResponseSerializer,
    UpdateStockItemResponseSerializer,
    RetrieveStockItemResponseSerializer,
    ListStockItemResponseSerializer,
    PaginatedStockItemResponseSerializer,
)
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


@extend_schema(tags=["Inventory"])
class StockItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stock items.

    Provides CRUD operations for inventory items (ingredients, utensils, containers).
    """

    permission_classes = [IsAuthenticated]
    serializer_class = StockItemSerializer
    queryset = StockItem.objects.all()

    @extend_schema(
        operation_id="list_stock_items",
        summary="List all stock items",
        description="Retrieves a list of all stock items with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="category",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by category (INGREDIENT, UTENSIL, CONTAINER, OTHER)",
                required=False,
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by item name",
                required=False,
            ),
        ],
        responses={
            200: PaginatedStockItemResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def list(self, request, *args, **kwargs):
        """List all stock items with optional filtering."""
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is requesting stock item list.")

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        response_data = PaginatedStockItemResponseSerializer(serializer.data).data
        logger.info(f"Returning {len(queryset)} items.")
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_stock_item",
        summary="Get stock item details",
        description="Retrieves detailed information for a specific stock item.",
        responses={
            200: RetrieveStockItemResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific stock item."""
        instance = self.get_object()
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(
            f"User {user_id} is requesting details for stock item ID: {instance.id}."
        )

        serializer = self.get_serializer(instance)
        response_data = RetrieveStockItemResponseSerializer(serializer.data).data
        logger.info(f"Returning details for stock item ID: {instance.id}.")
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_stock_item",
        summary="Create new stock item",
        description="Creates a new stock item with the provided information.",
        request=StockItemSerializer,
        responses={
            201: CreateStockItemResponseSerializer,
            400: ValidationErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def create(self, request, *args, **kwargs):
        """Create a new stock item."""
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
        response_data = CreateStockItemResponseSerializer(
            self.get_serializer(created_stock_item).data
        ).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_stock_item",
        summary="Update stock item",
        description="Updates an existing stock item. Supports partial updates.",
        request=StockItemSerializer,
        responses={
            200: UpdateStockItemResponseSerializer,
            400: ValidationErrorResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def update(self, request, *args, **kwargs):
        """Update an existing stock item (full or partial)."""
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
        response_data = UpdateStockItemResponseSerializer(
            self.get_serializer(updated_stock_item).data
        ).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_stock_item",
        summary="Delete stock item",
        description="Permanently removes a stock item from the system.",
        responses={
            204: NoContentResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a stock item."""
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
        return Response(status=status.HTTP_204_NO_CONTENT)
