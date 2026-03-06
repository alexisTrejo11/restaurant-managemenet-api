import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ..serializers import (
    StockTransactionSerializer,
    CreateTransactionResponseSerializer,
    UpdateTransactionResponseSerializer,
)
from ..services.stock_transaction_service import (
    StockTransactionService as TransactionService,
)
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


@extend_schema(
    operation_id="register_stock_transaction",
    summary="Register stock transaction",
    description="Records a new stock transaction (IN or OUT) and updates inventory levels.",
    request=StockTransactionSerializer,
    responses={
        201: CreateTransactionResponseSerializer,
        400: ValidationErrorResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Inventory Transactions"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_transaction(request):
    """Register a new stock transaction."""
    user_id = request.user.id
    logger.info(f"User {user_id} is requesting to register a stock transaction")

    serializer = StockTransactionSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)

    transaction = TransactionService.process_transaction(serializer.validated_data)

    logger.info(
        f"Transaction ID: {transaction.id} for Stock {transaction.stock.id} created successfully by user {user_id}."
    )

    transaction_serialized = StockTransactionSerializer(transaction)
    response_data = CreateTransactionResponseSerializer(
        transaction_serialized.data
    ).data
    return Response(response_data, status=status.HTTP_201_CREATED)


@extend_schema(
    operation_id="update_stock_transaction",
    summary="Update stock transaction",
    description="Updates an existing stock transaction details.",
    request=StockTransactionSerializer,
    responses={
        200: UpdateTransactionResponseSerializer,
        400: ValidationErrorResponseSerializer,
        404: NotFoundErrorResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Inventory Transactions"],
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_transaction(request, transaction_id):
    """Update an existing stock transaction."""
    user_id = request.user.id
    logger.info(
        f"User {user_id} is requesting to update stock transaction {transaction_id}"
    )

    serializer = StockTransactionSerializer(
        data=request.data, context={"request": request}
    )
    serializer.is_valid(raise_exception=True)

    existing_transaction = TransactionService.get_transaction(transaction_id)
    transaction_updated = TransactionService.update_transaction(
        existing_transaction, serializer.validated_data
    )

    logger.info(
        f"Transaction ID: {transaction_updated.id} for Stock {transaction_updated.stock.id} updated successfully by user {user_id}."
    )

    transaction_serialized = StockTransactionSerializer(transaction_updated)
    response_data = UpdateTransactionResponseSerializer(
        transaction_serialized.data
    ).data
    return Response(response_data, status=status.HTTP_200_OK)


@extend_schema(
    operation_id="delete_stock_transaction",
    summary="Delete stock transaction",
    description="Permanently removes a stock transaction from the system.",
    responses={
        204: NoContentResponseSerializer,
        404: NotFoundErrorResponseSerializer,
        **COMMON_RESPONSES,
    },
    tags=["Inventory Transactions"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_transaction(request, transaction_id):
    """Delete a stock transaction."""
    user_id = request.user.id
    logger.info(
        f"User {user_id} is requesting to delete stock transaction {transaction_id}"
    )

    transaction_to_delete = TransactionService.get_transaction(transaction_id)
    TransactionService.delete_transaction(transaction_to_delete)

    logger.info(
        f"Transaction ID: {transaction_id} deleted successfully by user {user_id}."
    )

    return Response(status=status.HTTP_204_NO_CONTENT)
