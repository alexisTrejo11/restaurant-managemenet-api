from drf_yasg import openapi
from ..serializers import UserResponseSerializer, UserCreateUpdateSerializer
from apps.shared.open_api.error_response_schema import (
    ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
    ErrorResponses,
)


class UserDocumentationData:
    """
    Documentation data for UserModelViewSet endpoints
    """

    user_response = openapi.Response(
        description="User response",
        schema=UserResponseSerializer,
        examples={
            "application/json": {
                "success": True,
                "message": "Operation successful",
                "data": {
                    "id": 1,
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "role": "CUSTOMER",
                    "gender": "MALE",
                    "phone_number": "+1234567890",
                    "birth_date": "1990-01-01",
                    "is_active": True,
                    "joined_at": "2023-01-01T12:00:00Z",
                    "last_login": "2023-01-01T12:00:00Z",
                },
            }
        },
    )

    user_list_response = openapi.Response(
        description="Paginated list of users",
        schema=UserResponseSerializer(many=True),
        examples={
            "application/json": {
                "success": True,
                "message": "Found 10 users",
                "data": [
                    {
                        "id": 1,
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com",
                        "role": "CUSTOMER",
                    },
                    {
                        "id": 2,
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "email": "jane.smith@example.com",
                        "role": "STAFF",
                    },
                ],
                "count": 10,
                "next": "http://api.example.com/users/?page=2",
                "previous": None,
            }
        },
    )

    not_found_response = openapi.Response(
        description="User not found",
        schema=NotFoundErrorResponseSerializer,
        examples={
            "application/json": {
                "success": False,
                "message": "User not found",
                "errors": {"detail": "User with ID 999 does not exist."},
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
                    "email": ["This email is already registered."],
                    "password": ["Password must be at least 8 characters."],
                },
            }
        },
    )

    success_no_data_response = ErrorResponses.get_success_operation()
    server_error_reponse = ErrorResponses.get_server_error_response()
    unauthorized_reponse = ErrorResponses.get_unauthorized_response()
    forbidden_reponse = ErrorResponses.get_forbidden_response()

    list_operation_summary = "List all users"
    list_operation_description = """
    Returns a paginated list of all users in the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can access this endpoint
    
    **Pagination:**
    - Default page size: 20
    - Customize with `?page_size` parameter
    
    **Filtering:**
    - Filter by role: `?role=STAFF`
    - Filter by active status: `?is_active=true`
    """

    retrieve_operation_summary = "Retrieve a user"
    retrieve_operation_description = """
    Returns detailed information about a specific user.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can access this endpoint
    """

    create_operation_summary = "Create a new user"
    create_operation_description = """
    Creates a new user in the system.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can create users
    
    **Required Fields:**
    - `first_name`: User's first name
    - `last_name`: User's last name
    - `email`: Unique email address
    - `password`: Account password
    - `role`: User role (CUSTOMER/STAFF/ADMIN)
    
    **Note:**
    - Password will be hashed before storage
    - Email must be unique
    """

    update_operation_summary = "Update a user"
    update_operation_description = """
    Updates an existing user.
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can update users
    
    **Note:**
    - Supports partial updates (PATCH)
    - Email cannot be changed to an already registered address
    - Password updates will trigger re-hashing
    """

    destroy_operation_summary = "Delete a user"
    destroy_operation_description = """
    Deactivates a user account (soft delete).
    
    **Permissions:**
    - `IsAdminUser`: Only admin users can delete users
    
    **Note:**
    - Performs a soft-delete (sets is_active=False)
    - User record remains in database
    - Can be reactivated by admin
    """
