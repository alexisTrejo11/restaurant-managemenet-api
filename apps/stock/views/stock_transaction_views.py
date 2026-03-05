from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import StockTransactionSerializer as TransactionSerializer
from ..services.stock_transaction_service import (
    StockTransactionService as TransactionService,
)
from ..documentation.stock_transaction_data import (
    StockTransactionDocumentationData as transactionDocData,
)
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from apps.shared.response import ResponseWrapper
import logging

logger = logging.getLogger(__name__)


@swagger_auto_schema(
    method="post",
    operation_id="register_stock_transaction",
    operation_summary=transactionDocData.register_operation_summary,
    operation_description=transactionDocData.register_operation_description,
    request_body=TransactionSerializer,
    responses={
        status.HTTP_201_CREATED: transactionDocData.transaction_response,
        status.HTTP_400_BAD_REQUEST: transactionDocData.validation_error_response,
        status.HTTP_401_UNAUTHORIZED: transactionDocData.unauthorized_reponse,
        status.HTTP_500_INTERNAL_SERVER_ERROR: transactionDocData.server_error_reponse,
    },
    tags=["Inventory Transactions"],
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_transaction(request):
    user_id = request.user.id
    logger.info(f"User {user_id} is requesting to register a stock transaction")

    serializer = TransactionSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)

    transaction = TransactionService.process_transaction(serializer.validated_data)

    logger.info(
        f"Transaction ID: {transaction.id} for Stock {transaction.stock.id} created successfully by user {user_id}."
    )

    transaction_serialized = TransactionSerializer(transaction)
    return ResponseWrapper.created(
        data=transaction_serialized.data, entity="Stock Transaction"
    )


@swagger_auto_schema(
    method="put",
    operation_id="update_stock_transaction",
    operation_summary=transactionDocData.update_operation_summary,
    operation_description=transactionDocData.update_operation_description,
    request_body=TransactionSerializer,
    responses={
        status.HTTP_200_OK: transactionDocData.transaction_response,
        status.HTTP_400_BAD_REQUEST: transactionDocData.validation_error_response,
        status.HTTP_401_UNAUTHORIZED: transactionDocData.unauthorized_reponse,
        status.HTTP_404_NOT_FOUND: transactionDocData.not_found_response,
        status.HTTP_500_INTERNAL_SERVER_ERROR: transactionDocData.server_error_reponse,
    },
    tags=["Inventory Transactions"],
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_transaction(request, transaction_id):
    user_id = request.user.id
    logger.info(
        f"User {user_id} is requesting to update stock transaction {transaction_id}"
    )

    serializer = TransactionSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)

    existing_transaction = TransactionService.get_transaction(transaction_id)
    transaction_updated = TransactionService.update_transaction(
        existing_transaction, serializer.validated_data
    )

    logger.info(
        f"Transaction ID: {transaction_updated.id} for Stock {transaction_updated.stock.id} updated successfully by user {user_id}."
    )

    transaction_serialized = TransactionSerializer(transaction_updated)
    return ResponseWrapper.updated(
        data=transaction_serialized.data, entity="Stock Transaction"
    )


@swagger_auto_schema(
    method="delete",
    operation_id="delete_stock_transaction",
    operation_summary=transactionDocData.delete_operation_summary,
    operation_description=transactionDocData.delete_operation_description,
    responses={
        status.HTTP_204_NO_CONTENT: "Transaction deleted successfully",
        status.HTTP_401_UNAUTHORIZED: transactionDocData.unauthorized_reponse,
        status.HTTP_404_NOT_FOUND: transactionDocData.not_found_response,
        status.HTTP_500_INTERNAL_SERVER_ERROR: transactionDocData.server_error_reponse,
    },
    tags=["Inventory Transactions"],
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_transaction(request, transaction_id):
    user_id = request.user.id
    logger.info(
        f"User {user_id} is requesting to delete stock transaction {transaction_id}"
    )

    transaction_to_delete = TransactionService.get_transaction(transaction_id)
    TransactionService.delete_transaction(transaction_to_delete)

    logger.info(
        f"Transaction ID: {transaction_id} deleted successfully by user {user_id}."
    )

    return ResponseWrapper.deleted(entity="Stock Transaction")
