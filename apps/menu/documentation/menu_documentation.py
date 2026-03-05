from drf_yasg import openapi
from ..serializers import DishSerializer
from apps.shared.open_api.error_response_schema import (
    ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
    ErrorResponses,
)


class DishDocumentationData:
    """
    Documentation data for DishViewSet endpoints
    """

    # Common responses
    dish_response = openapi.Response(
        description="Dish response",
        schema=DishSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "name": "Margherita Pizza",
                    "description": "Classic pizza with tomato sauce and mozzarella",
                    "price": "12.99",
                    "category": "PIZZA",
                    "status": "ACTIVE",
                    "image": "https://example.com/pizza.jpg",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                },
            }
        },
    )

    dish_list_response = openapi.Response(
        description="List of dishes",
        schema=DishSerializer(many=True),
        examples={
            "application/json": {
                "success": True,
                "message": "Found 5 dishes",
                "data": [
                    {
                        "id": 1,
                        "name": "Margherita Pizza",
                        "price": "12.99",
                        "category": "PIZZA",
                    },
                    {
                        "id": 2,
                        "name": "Caesar Salad",
                        "price": "8.99",
                        "category": "SALAD",
                    },
                ],
                "metadata": {
                    "total_items": 5,
                    "filters_applied": {"category": ["PIZZA"]},
                },
            }
        },
    )

    not_found_response = openapi.Response(
        description="Dish not found",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Dish not found",
                "errors": {"detail": "Dish with ID 999 does not exist."},
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
                    "price": ["Price must be positive."],
                    "category": ["Invalid category specified."],
                },
            }
        },
    )

    success_no_data = ErrorResponses.get_success_operation()
    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    list_operation_summary = "List all dishes"
    list_operation_description = """
    Returns a paginated list of all active dishes in the menu.
    
    **Permissions:**
    - Public access (no authentication required)
    
    **Filtering:**
    - Filter by category: `?category=PIZZA`
    - Filter by price range: `?price_min=10&price_max=20`
    - Filter by status: `?status=ACTIVE` (default)
    
    **Searching:**
    - Search by name or description: `?search=margherita`
    
    **Ordering:**
    - Sort by name, price or date: `?ordering=price` or `?ordering=-created_at`
    """

    retrieve_operation_summary = "Retrieve a dish"
    retrieve_operation_description = """
    Returns detailed information about a specific dish.
    
    **Permissions:**
    - Public access (no authentication required)
    """

    create_operation_summary = "Create a new dish"
    create_operation_description = """
    Creates a new dish in the menu.
    
    **Permissions:**
    - `IsAuthenticated`: Staff access required
    
    **Required Fields:**
    - `name`: Dish name
    - `price`: Price (decimal)
    - `category`: Dish category
    
    **Note:**
    - Default status is ACTIVE
    """

    update_operation_summary = "Update a dish"
    update_operation_description = """
    Updates an existing dish.
    
    **Permissions:**
    - `IsAuthenticated`: Staff access required
    
    **Note:**
    - Supports both PUT (full update) and PATCH (partial update)
    - Cannot change status to DELETED (use DELETE instead)
    """

    destroy_operation_summary = "Delete a dish"
    destroy_operation_description = """
    Removes a dish from the menu.
    
    **Permissions:**
    - `IsAuthenticated`: Staff access required
    
    **Note:**
    - Actually performs a soft-delete (sets status to DELETED)
    - Dish remains in database but won't appear in listings
    """
