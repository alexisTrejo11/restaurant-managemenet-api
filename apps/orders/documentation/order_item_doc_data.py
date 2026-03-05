from drf_yasg import openapi
from ..serializers import OrderItemSerializer
from apps.shared.open_api.error_response_schema import (
    ErrorResponses,
    NotFoundErrorResponseSerializer,
    ValidationErrorResponseSerializer,
)


class OrderItemDocumentationData:
    not_found_response = openapi.Response(
        description="Not Found - The requested order item does not exist.",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {"success": False, "message": "Order Item not found."}
        },
    )

    validation_error_response = openapi.Response(
        description="Bad Request - Invalid input data.",
        schema=ValidationErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Validation Error",
                "errors": {
                    "menu_item": ["This field is required."],
                    "quantity": ["Ensure this value is greater than or equal to 1."],
                },
            }
        },
    )

    success_no_data_response = ErrorResponses.get_success_operation()
    server_error_response = ErrorResponses.get_server_error_response()
    unauthorized_response = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    order_items_list_response = openapi.Response(
        description="List of order items after addition",
        schema=OrderItemSerializer(many=True),
        examples={
            "application/json": [
                {
                    "id": 1,
                    "menu_item": 5,
                    "order": 10,
                    "menu_extra": 3,
                    "quantity": 2,
                    "notes": "No onions please",
                    "is_delivered": False,
                    "added_at": "2023-01-15T14:30:00Z",
                },
                {
                    "id": 2,
                    "menu_item": 7,
                    "order": 10,
                    "menu_extra": None,
                    "quantity": 1,
                    "notes": "",
                    "is_delivered": True,
                    "added_at": "2023-01-15T14:35:00Z",
                },
            ]
        },
    )

    add_items_validation_error_response = openapi.Response(
        description="Bad Request - Invalid input data for items.",
        schema=ValidationErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Validation Error",
                "errors": [
                    {
                        "menu_item": ["This field is required."],
                        "quantity": [
                            "Ensure this value is greater than or equal to 1."
                        ],
                    }
                ],
            }
        },
    )

    order_not_found_response = openapi.Response(
        description="Not Found - The specified order does not exist.",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {"success": False, "message": "Order not found."}
        },
    )

    # Delete items specific responses
    delete_items_validation_error_response = openapi.Response(
        description="Bad Request - Missing or invalid order/item IDs.",
        schema=ValidationErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Both Order ID and Order Item IDs are required",
            }
        },
    )

    order_or_items_not_found_response = openapi.Response(
        description="Not Found - The specified order or items do not exist.",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Order or some items not found.",
            }
        },
    )

    add_items_operation_summary = "Add items to an order"
    add_items_operation_description = """
        Adds one or more items to an existing order.
        
        **Permissions:**
        - `IsAuthenticated`: Only authenticated users can access this endpoint.
        
        **Request Body:**
        Expects an array of order item objects to be added to the order.
        
        **Parameters:**
        - `order_id`: The ID of the order to which items will be added (path parameter)
        """
    add_items_operation_id = "Add Order Items"

    delete_items_operation_summary = "Delete items from an order"
    delete_items_operation_description = """
        Removes one or more items from an existing order.
        
        **Permissions:**
        - `IsAuthenticated`: Only authenticated users can access this endpoint.
        
        **Request Body:**
        Expects an object with an `order_item_ids` array containing the IDs of items to remove.
        
        **Parameters:**
        - `order_id`: The ID of the order from which items will be removed (path parameter)
        """
    delete_items_operation_id = "Delete Order Items"
