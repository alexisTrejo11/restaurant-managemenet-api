from drf_yasg import openapi
from ..serializers import TableSerializer
from apps.shared.response.api_response_serializers import (
    ApiResponseSerializer,
    NotFoundErrorResponseSerializer,
    ValidationErrorResponseSerializer,
)
from rest_framework import serializers
from apps.shared.open_api.error_response_schema import ErrorResponses


# TODO: Delete
class ApiResponseWithDataSerializer(ApiResponseSerializer):
    """
    Serializer for successful responses with data
    """

    data = serializers.DictField()


class TableListResponseSerializer(ApiResponseWithDataSerializer):
    """
    Serializer for table list responses
    """

    data = serializers.ListField(child=TableSerializer())


class TableDocumentationData:
    """
    Documentation data for TableViews endpoints
    """

    # 2XX
    success_response = openapi.Response(
        description="Successful operation",
        schema=TableListResponseSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "number": "T-001",
                    "capacity": 4,
                    "status": "available",
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z",
                },
            }
        },
    )
    list_response = openapi.Response(
        description="List of all tables",
        schema=TableListResponseSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Found 3 tables",
                "data": [
                    {"id": 1, "number": "T-001", "capacity": 4, "status": "available"},
                    {"id": 2, "number": "T-002", "capacity": 6, "status": "occupied"},
                ],
            }
        },
    )

    # 4XX
    not_found_response = openapi.Response(
        description="Table not found",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "Table not found",
                "errors": {"detail": "Table with number T-999 does not exist."},
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
                    "capacity": ["Capacity must be at least 2."],
                    "number": ["This table number already exists."],
                },
            }
        },
    )
    success_no_data_response = ErrorResponses.get_success_operation()
    forbidden_response = ErrorResponses.get_forbidden_response()
    unauthorized_response = ErrorResponses.get_unauthorized_response()

    # 5XX
    server_error_response = ErrorResponses.get_server_error_response()

    # Helping Texts
    list_operation_summary = "List all tables"
    list_operation_description = """
    Returns a list of all tables in the system.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    
    **Filtering:**
    - You can filter by status using query parameters: `?status=available`
    """

    retrieve_operation_summary = "Retrieve a specific table"
    retrieve_operation_description = """
    Returns details for a specific table identified by its number.
    
    **Permissions:**
    - `IsAuthenticated`: User must be logged in.
    """

    create_operation_summary = "Create a new table"
    create_operation_description = """
    Creates a new table in the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can create tables.
    
    **Required Fields:**
    - `number`: Unique identifier for the table
    - `capacity`: Number of seats
    - `status`: Current status (available, occupied, reserved, etc.)
    """

    update_operation_summary = "Update an existing table"
    update_operation_description = """
    Updates an existing table identified by its number.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can update tables.
    
    **Partial Updates:**
    - Supports PATCH for partial updates
    """

    destroy_operation_summary = "Delete a table"
    destroy_operation_description = """
    Deletes a table from the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can delete tables.
    
    **Note:**
    - This action is irreversible
    """
