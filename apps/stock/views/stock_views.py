from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import NotFound
from apps.shared.response import ResponseWrapper
from rest_framework.permissions import IsAuthenticated
import logging
from ..models import Stock
from ..serializers import StockSerializer
from ..services.stock_service import StockService
from ..documentation.stock_doc_data import StockDocumentationData as StockDocData
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from apps.shared.open_api.error_response_schema import ErrorResponses as GenericResponse

logger = logging.getLogger(__name__)


class StockViews(ViewSet):
    queryset = Stock.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    @swagger_auto_schema(
        operation_id="list_stock_items",
        operation_summary=StockDocData.list_operation_summary,
        operation_description=StockDocData.list_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "include_transactions",
                openapi.IN_QUERY,
                description="Include transaction history",
                type=openapi.TYPE_BOOLEAN,
            )
        ],
        responses={
            status.HTTP_200_OK: StockDocData.list_response,
            status.HTTP_401_UNAUTHORIZED: GenericResponse.get_unauthorized_response(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: GenericResponse.get_server_error_response(),
        },
        tags=["Inventory"],
    )
    def list(self, request):
        queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)

        logger.info(f"Listed {len(queryset)} stock items")

        return ResponseWrapper.success(
            data=serializer.data,
            metadata={
                "total_items": queryset.count(),
                "note": "Add ?include_transactions=true to include transactions",
            },
        )

    @swagger_auto_schema(
        operation_id="retrieve_stock_item",
        operation_summary=StockDocData.retrieve_operation_summary,
        operation_description=StockDocData.retrieve_operation_description,
        manual_parameters=[
            openapi.Parameter(
                "include_transactions",
                openapi.IN_QUERY,
                description="Include transaction history",
                type=openapi.TYPE_BOOLEAN,
            )
        ],
        responses={
            status.HTTP_200_OK: StockDocData.success_response,
            status.HTTP_404_NOT_FOUND: StockDocData.not_found_response,
            status.HTTP_401_UNAUTHORIZED: GenericResponse.get_unauthorized_response(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: GenericResponse.get_server_error_response(),
        },
        tags=["Inventory"],
    )
    def retrieve(self, request, pk=None):
        stock = self.get_stock_or_404(pk)
        serializer = self.get_serializer(stock)

        logger.info(
            f"Retrieved stock {stock.id} with transactions={request.query_params.get('include_transactions')}"
        )

        return ResponseWrapper.found(
            data=serializer.data, entity=f"Stock {stock.id} Details"
        )

    @swagger_auto_schema(
        operation_id="create_stock_item",
        operation_summary=StockDocData.create_operation_summary,
        operation_description=StockDocData.create_operation_description,
        request_body=StockSerializer,
        responses={
            status.HTTP_201_CREATED: StockDocData.success_response,
            status.HTTP_400_BAD_REQUEST: StockDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: GenericResponse.get_unauthorized_response(),
            status.HTTP_500_INTERNAL_SERVER_ERROR: GenericResponse.get_server_error_response(),
        },
        tags=["Inventory"],
    )
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stock_created = StockService.create_stock(serializer.validated_data)

        stock_serialized = self.get_serializer(stock_created)
        return ResponseWrapper.created(data=stock_serialized.data, entity="Stock")

    @swagger_auto_schema(
        operation_id="update_stock_item",
        operation_summary=StockDocData.update_operation_summary,
        operation_description=StockDocData.update_operation_description,
        request_body=StockSerializer,
        responses={
            status.HTTP_200_OK: StockDocData.success_response,
            status.HTTP_400_BAD_REQUEST: StockDocData.validation_error_response,
            status.HTTP_401_UNAUTHORIZED: GenericResponse.get_unauthorized_response(),
            status.HTTP_404_NOT_FOUND: StockDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: GenericResponse.get_server_error_response(),
        },
        tags=["Inventory"],
    )
    def update(self, request, pk=None):
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
        serializer = self.get_serializer(stock, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)

        updated_stock = StockService.update_stock(
            instance=stock,
            validated_data=serializer.validated_data,
        )
        stock_serializer = self.get_serializer(updated_stock)

        return ResponseWrapper.updated(
            data=stock_serializer.data,
            entity=f"Stock {updated_stock.id}",
            metadata={"updated_fields": list(serializer.validated_data.keys())},
        )

    @swagger_auto_schema(
        operation_id="delete_stock_item",
        operation_summary=StockDocData.destroy_operation_summary,
        operation_description=StockDocData.destroy_operation_description,
        responses={
            status.HTTP_200_OK: GenericResponse.get_success_operation(),
            status.HTTP_401_UNAUTHORIZED: GenericResponse.get_unauthorized_response(),
            status.HTTP_404_NOT_FOUND: StockDocData.not_found_response,
            status.HTTP_500_INTERNAL_SERVER_ERROR: GenericResponse.get_server_error_response(),
        },
        tags=["Inventory"],
    )
    def destroy(self, request, pk=None):
        stock = self.get_stock_or_404(pk)
        user_id = getattr(request.user, "id", "Anonymous")
        logger.info(f"User {user_id} is attempting to delete stock ID: {stock.id}.")

        stock_id = stock.id
        StockService.delete_stock(stock)

        logger.info(f"Stock ID: {stock_id} deleted successfully by user {user_id}.")
        return ResponseWrapper.deleted(
            entity=f"Stock {stock_id}",
        )

    def get_stock_or_404(self, pk) -> Stock:
        """Helper method with logging for object retrieval"""
        try:
            obj = self.queryset.get(pk=pk)
            logger.debug(f"Successfully retrieved stock ID: {obj.id}")
            return obj
        except Stock.DoesNotExist:
            logger.error(f"Stock not found. ID: {pk}")
            raise NotFound("Stock not found")
