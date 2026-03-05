from ..serializers import StockItemSerializer
from drf_yasg import openapi
from apps.shared.open_api.error_response_schema import (
    ValidationErrorResponseSerializer,
    ErrorResponses,
)


class StockItemDocumentationData:
    """
    Documentation data for StockItemViewSet endpoints
    """

    success_response = openapi.Response(
        description="Successful operation",
        schema=StockItemSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "name": "Premium Coffee Beans",
                    "description": "Arabica beans from Colombia",
                    "unit": "kg",
                    "category": "coffee",
                    "supplier": "Colombian Coffee Co.",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                },
            }
        },
    )

    list_response = openapi.Response(
        description="List of all stock items",
        schema=StockItemSerializer(many=True),
        examples={
            "application/json": {
                "success": True,
                "message": "Found 5 stock items",
                "data": [
                    {
                        "id": 1,
                        "name": "Premium Coffee Beans",
                        "unit": "kg",
                        "category": "coffee",
                    },
                    {
                        "id": 2,
                        "name": "Organic Milk",
                        "unit": "liter",
                        "category": "dairy",
                    },
                ],
            }
        },
    )

    not_found_response = openapi.Response(
        description="Stock item not found",
        schema=ValidationErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Stock item not found",
                "errors": {"detail": "Stock item with ID 999 does not exist."},
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
                    "name": ["This field is required."],
                    "unit": ["Invalid unit specified."],
                },
            }
        },
    )
    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    # Operation metadata
    list_operation_summary = "List all stock items"
    list_operation_description = """
    Returns a paginated list of all stock items in inventory.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Filtering:**
    - You can filter by category using query parameters: `?category=coffee`
    - Filter by supplier: `?supplier=Colombian+Coffee+Co`
    """

    retrieve_operation_summary = "Retrieve a specific stock item"
    retrieve_operation_description = """
    Returns detailed information about a specific stock item.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    """

    create_operation_summary = "Create a new stock item"
    create_operation_description = """
    Creates a new stock item in the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can create stock items.
    
    **Required Fields:**
    - `name`: Name of the item
    - `unit`: Measurement unit (kg, liter, piece, etc.)
    - `category`: Item category
    """

    update_operation_summary = "Update a stock item"
    update_operation_description = """
    Updates an existing stock item.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can update stock items.
    
    **Note:**
    - Supports both PUT (full update) and PATCH (partial update)
    """

    destroy_operation_summary = "Delete a stock item"
    destroy_operation_description = """
    Deletes a stock item from the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can delete stock items.
    
    **Note:**
    - This action is irreversible
    - Associated stock records will be preserved but will reference a deleted item
    """
