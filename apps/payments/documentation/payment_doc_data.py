from drf_yasg import openapi
from ..serializers import PaymentSerializer
from apps.shared.open_api.error_response_schema import (
    NotFoundErrorResponseSerializer,
    ValidationErrorResponseSerializer,
    ErrorResponses,
)


class PaymentDocumentationData:
    """
    Documentation data for PaymentAdminViews endpoints
    """

    # Common responses
    payment_response = openapi.Response(
        description="Payment response",
        schema=PaymentSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "order": 101,
                    "amount": "49.99",
                    "payment_method": "CREDIT_CARD",
                    "status": "COMPLETED",
                    "transaction_id": "txn_123456789",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                },
            }
        },
    )

    payment_list_response = openapi.Response(
        description="Paginated list of payments",
        schema=PaymentSerializer(many=True),
        examples={
            "application/json": {
                "success": True,
                "message": "Found 5 payments",
                "data": [
                    {
                        "id": 1,
                        "order": 101,
                        "amount": "49.99",
                        "payment_method": "CREDIT_CARD",
                        "status": "COMPLETED",
                    },
                    {
                        "id": 2,
                        "order": 102,
                        "amount": "29.99",
                        "payment_method": "PAYPAL",
                        "status": "PENDING",
                    },
                ],
                "metadata": {
                    "pagination": {
                        "count": 5,
                        "next": "http://api.example.com/payments/?page=2",
                        "previous": None,
                    },
                    "applied_filters": ["status=COMPLETED"],
                },
            }
        },
    )

    not_found_response = openapi.Response(
        description="Payment not found",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Payment not found",
                "errors": {"detail": "Payment with ID 999 does not exist."},
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
                    "amount": ["Amount must be positive."],
                    "payment_method": ["Invalid payment method specified."],
                },
            }
        },
    )

    success_no_data = ErrorResponses.get_success_operation()
    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    # Operation metadata
    list_operation_summary = "List all payments"
    list_operation_description = """
    Returns a paginated list of all payments in the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can access this endpoint
    
    **Pagination:**
    - Custom page size available via `?page_size` parameter
    
    **Filtering:**
    - Filter by status: `?status=COMPLETED`
    - Filter by payment method: `?payment_method=CREDIT_CARD`
    - Filter by date range: `?start_date=2023-01-01&end_date=2023-01-31`
    - Filter by amount range: `?min_amount=10&max_amount=100`
    """

    retrieve_operation_summary = "Retrieve a payment"
    retrieve_operation_description = """
    Returns detailed information about a specific payment.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can access this endpoint
    """

    create_operation_summary = "Create a payment record"
    create_operation_description = """
    Creates a new payment record in the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can create payments
    
    **Required Fields:**
    - `order`: Associated order ID
    - `amount`: Payment amount
    - `payment_method`: Payment method (CREDIT_CARD/PAYPAL/etc.)
    - `status`: Payment status
    
    **Note:**
    - Typically payments are created automatically during checkout
    - Manual creation should only be done for special cases
    """

    update_operation_summary = "Update a payment record"
    update_operation_description = """
    Updates an existing payment record.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can update payments
    
    **Note:**
    - Use with caution as payments are financial records
    - Some fields like transaction_id may be immutable
    """

    destroy_operation_summary = "Delete a payment record"
    destroy_operation_description = """
    Deletes a payment record from the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can delete payments
    
    **Query Parameters:**
    - `hard_delete=true`: Permanently delete record (default is soft delete)
    
    **Note:**
    - Default behavior is soft delete (sets inactive flag)
    - Hard delete permanently removes the record
    - Financial regulations may require keeping payment records
    """
