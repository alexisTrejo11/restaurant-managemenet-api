import logging
from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..models import Stock
from ..serializers import (
    StockSerializer,
    CreateStockResponseSerializer,
    UpdateStockResponseSerializer,
    RetrieveStockResponseSerializer,
    ListStockResponseSerializer,
    PaginatedStockResponseSerializer,
)
from ..services.stock_service import StockService
from apps.shared.response import (
    NoContentResponseSerializer,
    ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
    UnauthorizedErrorResponseSerializer,
    ServerErrorResponseSerializer,
)

logger = logging.getLogger(__name__)

COMMON_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: UnauthorizedErrorResponseSerializer,
    status.HTTP_500_INTERNAL_SERVER_ERROR: ServerErrorResponseSerializer,
}


@extend_schema(tags=["Inventory"])
class StockViews(ViewSet):
    """
    ViewSet for managing stock inventory.

    Provides CRUD operations for stock records with optional transaction history.
    """

    queryset = Stock.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    @extend_schema(
        operation_id="list_stocks",
        summary="List all stocks",
        description="Retrieves a list of all stock records with pagination support.",
        parameters=[
            OpenApiParameter(
                name="include_transactions",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Include transaction history for each stock",
                required=False,
            ),
        ],
        responses={
            200: PaginatedStockResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def list(self, request):
        """List all stocks with optional transaction history."""
        queryset = self.queryset
        page = None

        # Try to paginate
        paginator = getattr(self, "paginator", None)
        if paginator:
            page = paginator.paginate_queryset(queryset, request)
            if page is not None:
                serializer = self.serializer_class(
                    page, many=True, context={"request": request}
                )
                return paginator.get_paginated_response(serializer.data)

        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        response_data = PaginatedStockResponseSerializer(serializer.data).data
        logger.info(f"Listed {len(queryset)} stock items")
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="retrieve_stock",
        summary="Get stock details",
        description="Retrieves detailed information for a specific stock record.",
        parameters=[
            OpenApiParameter(
                name="include_transactions",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Include transaction history",
                required=False,
            ),
        ],
        responses={
            200: RetrieveStockResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def retrieve(self, request, pk=None):
        """Retrieve a specific stock record."""
        stock = self.get_stock_or_404(pk)
        serializer = self.serializer_class(stock, context={"request": request})
        response_data = RetrieveStockResponseSerializer(serializer.data).data
        logger.info(
            f"Retrieved stock {stock.id} with include_transactions={request.query_params.get('include_transactions')}"
        )
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="create_stock",
        summary="Create new stock",
        description="Creates a new stock record for an inventory item.",
        request=StockSerializer,
        responses={
            201: CreateStockResponseSerializer,
            400: ValidationErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def create(self, request):
        """Create a new stock record."""
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        stock_created = StockService.create_stock(serializer.validated_data)

        stock_serialized = self.serializer_class(
            stock_created, context={"request": request}
        )
        response_data = CreateStockResponseSerializer(stock_serialized.data).data
        return Response(response_data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="update_stock",
        summary="Update stock",
        description="Updates an existing stock record. Supports partial updates.",
        request=StockSerializer,
        responses={
            200: UpdateStockResponseSerializer,
            400: ValidationErrorResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def update(self, request, pk=None):
        """Update an existing stock record."""
        user_id = request.user.id
        logger.info(
            f"User {user_id} attempting to update stock ID: {pk}",
            extra={
                "action": "update",
                "user": user_id,
                "stock_id": pk,
                "data": request.data,
            },
        )

        stock = self.get_stock_or_404(pk)
        serializer = self.serializer_class(
            stock, data=request.data, partial=False, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        updated_stock = StockService.update_stock(
            instance=stock,
            validated_data=serializer.validated_data,
        )
        stock_serializer = self.serializer_class(
            updated_stock, context={"request": request}
        )
        response_data = UpdateStockResponseSerializer(stock_serializer.data).data
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        operation_id="delete_stock",
        summary="Delete stock",
        description="Permanently removes a stock record from the system.",
        responses={
            204: NoContentResponseSerializer,
            404: NotFoundErrorResponseSerializer,
            **COMMON_RESPONSES,
        },
    )
    def destroy(self, request, pk=None):
        """Delete a stock record."""
        stock = self.get_stock_or_404(pk)
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is attempting to delete stock ID: {stock.id}.")

        stock_id = stock.id
        StockService.delete_stock(stock)

        logger.info(f"Stock ID: {stock_id} deleted successfully by user {user_id}.")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_stock_or_404(self, pk) -> Stock:
        """Helper method with logging for object retrieval"""
        try:
            obj = self.queryset.get(pk=pk)
            logger.debug(f"Successfully retrieved stock ID: {obj.id}")
            return obj
        except Stock.DoesNotExist:
            logger.error(f"Stock not found. ID: {pk}")
            raise NotFound("Stock not found")
