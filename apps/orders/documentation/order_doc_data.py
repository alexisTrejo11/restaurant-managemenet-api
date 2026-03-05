from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from ..serializers import OrderSerializer
from apps.shared.open_api.error_response_schema import (
    NotFoundErrorResponseSerializer,
    ValidationErrorResponseSerializer,
    ErrorResponses,
)
from apps.payments.serializers import PaymentSerializer


class OrderDocumentationData:
    """
    Documentation data for OrderViewsSet endpoints
    """

    order_response = openapi.Response(
        description="Order response",
        schema=OrderSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "table": 5,
                    "status": "IN_PROGRESS",
                    "created_at": "2023-01-01T12:00:00Z",
                    "end_at": None,
                    "order_items": [
                        {"menu_item": 101, "quantity": 2, "notes": "No onions please"}
                    ],
                },
            }
        },
    )

    order_list_response = openapi.Response(
        description="List of orders",
        schema=OrderSerializer(many=True),
        examples={
            "application/json": {
                "success": True,
                "message": "Found 3 orders",
                "data": [
                    {
                        "id": 1,
                        "table": 5,
                        "status": "IN_PROGRESS",
                        "created_at": "2023-01-01T12:00:00Z",
                    },
                    {
                        "id": 2,
                        "table": 3,
                        "status": "COMPLETED",
                        "created_at": "2023-01-01T11:00:00Z",
                        "end_at": "2023-01-01T12:30:00Z",
                    },
                ],
            }
        },
    )

    not_found_response = openapi.Response(
        description="Order not found",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Order not found",
                "errors": {"detail": "Order with ID 999 does not exist."},
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
                    "table": ["This table is currently occupied."],
                    "order_items": ["At least one item is required."],
                },
            }
        },
    )

    complete_order_response = openapi.Response(
        description="Order completion response",
        schema=PaymentSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Order 1 Successfully Completed. A Payment with Id 101 was initiated pending to be paid",
                "data": {"id": 101, "order": 1, "amount": "49.99", "status": "PENDING"},
            }
        },
    )

    success_no_data = ErrorResponses.get_success_operation()
    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    list_operation_summary = "List all orders"
    list_operation_description = """
    Returns a list of all orders in the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Filtering:**
    - Filter by status: `?status=COMPLETED`
    - Filter by table: `?table_id=5`
    """

    retrieve_operation_summary = "Retrieve an order"
    retrieve_operation_description = """
    Returns detailed information about a specific order including all order items.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    """

    create_operation_summary = "Create a new order"
    create_operation_description = """
    Creates a new order in the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Required Fields:**
    - `table`: Table ID
    - `order_items`: List of menu items with quantities
    
    **Note:**
    - Initial status will be IN_PROGRESS
    - Order items must reference valid menu items
    """

    update_operation_summary = "Update an order"
    update_operation_description = """
    Updates an existing order.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Query Parameters:**
    - `status`: New status (IN_PROGRESS/COMPLETED/CANCELLED)
    - `table_id`: New table ID
    
    **Note:**
    - Only certain status transitions are allowed
    - Table can only be changed if order is IN_PROGRESS
    """

    destroy_operation_summary = "Delete an order"
    destroy_operation_description = """
    Deletes an order from the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Note:**
    - Only orders with status IN_PROGRESS can be deleted
    - Completed orders should be archived, not deleted
    """

    complete_operation_summary = "Complete an order"
    complete_operation_description = """
    Marks an order as completed and initiates payment.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Note:**
    - Sets status to COMPLETED
    - Records completion timestamp
    - Automatically creates a payment record
    - Returns payment details
    """

    cancel_operation_summary = "Cancel an order"
    cancel_operation_description = """
    Marks an order as cancelled.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in
    
    **Note:**
    - Sets status to CANCELLED
    - Records cancellation timestamp
    - Cannot be undone
    """
