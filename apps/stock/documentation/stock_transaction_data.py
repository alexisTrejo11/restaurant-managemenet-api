from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from ..serializers import StockTransactionSerializer as TransactionSerializer
from apps.shared.open_api.error_response_schema import (
    ErrorResponses,
    ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
)


class StockTransactionDocumentationData:
    """
    Documentation data for Stock Transaction endpoints
    """

    # Common responses
    transaction_response = openapi.Response(
        description="Stock Transaction response",
        schema=TransactionSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "stock": 101,
                    "transaction_type": "in",
                    "quantity": 50,
                    "notes": "Received new shipment",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                },
            }
        },
    )

    not_found_response = openapi.Response(
        description="Transaction not found",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Transaction not found",
                "errors": {"detail": "Transaction with ID 999 does not exist."},
            }
        },
    )

    validation_error_response = openapi.Response(
        description="Validation error",
        schema=ValidationErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Validation Error",
                "errors": {
                    "quantity": ["Quantity must be positive."],
                    "transaction_type": ["Invalid transaction type."],
                },
            }
        },
    )
    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    # Operation metadata
    register_operation_summary = "Register a new stock transaction"
    register_operation_description = """
    Records a new stock movement (in/out) in the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Required Fields:**
    - `stock`: ID of the stock item
    - `transaction_type`: 'in' for incoming stock, 'out' for outgoing
    - `quantity`: Amount of stock moved
    
    **Note:**
    - This will automatically update the associated stock total
    """

    update_operation_summary = "Update a stock transaction"
    update_operation_description = """
    Updates an existing stock transaction record.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Note:**
    - Updating quantity will recalculate the associated stock total
    - Transaction type cannot be changed after creation
    """

    delete_operation_summary = "Delete a stock transaction"
    delete_operation_description = """
    Removes a stock transaction from the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Note:**
    - This will reverse the transaction's effect on stock totals
    - This action is irreversible
    """
