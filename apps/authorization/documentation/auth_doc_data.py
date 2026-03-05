from drf_yasg import openapi
from rest_framework import status
from apps.authorization.serializers import (
    LogoutResponseSerializer,
    ApiResponseWithTokensSerializer,
)
from apps.shared.open_api.error_response_schema import ErrorResponses

server_error_example = {
    "application/json": {
        "success": False,
        "message": "An unexpected error occurred.",
        "errors": {},
    }
}


class SignupDocumentationData:
    """
    A class that provides examples and messages to make views less verbose
    """

    signup_responses = {
        status.HTTP_200_OK: openapi.Response(
            description="User successfully registered and session created.",
            schema=ApiResponseWithTokensSerializer,
            examples={
                "application/json": {
                    "success": True,
                    "message": "Signup Successfully Processed",
                    "data": {
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3ODAwMDc5MCwiaWF0IjoxNjc3OTk3MTkwLCJqdGkiOiJmYzY4MGI0Yy0xYzQ3LTQzNjAtOTYyYi0xNDUzYzEwMTE4NjUiLCJ1c2VyX2idIjoxfQ.some_long_refresh_token_string",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc3OTk3NDkwLCJpYXQiOjE2Nzc5OTcxOTAsImp0aSI6ImRmN2VmYTczLTI1MTktNDUwMy1hYjYwLWU1Yjc0NzE0NWMwNiIsInVzZXJfaWQiOjEsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIn0.some_long_access_token_string",
                    },
                }
            },
        ),
        status.HTTP_400_BAD_REQUEST: ErrorResponses.get_validation_error_response(),
        **ErrorResponses.get_common_error_responses(),
    }

    singup_operation_description = """
        This endpoint allows new users to register an account.
        
        **Permissions:**
        - `AllowAny`: No authentication is required to access this endpoint.

        **Request Body:**
        The request body expects a JSON object containing the user's email, password, and password confirmation.
        """
    singup_operation_summary = "Register a new user"
    signup_method = "post"
    singup_operation_id = "User Registration"


class LoginDocumentationData:
    """
    A class that provides examples and messages to make views less verbose
    """

    responses = {
        status.HTTP_200_OK: openapi.Response(
            description="User successfully registered and session created.",
            schema=ApiResponseWithTokensSerializer,
            examples={
                "application/json": {
                    "success": True,
                    "message": "Login Successfully Processed",
                    "data": {
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY3ODAwMDc5MCwiaWF0IjoxNjc3OTk3MTkwLCJqdGkiOiJmYzY4MGI0Yy0xYzQ3LTQzNjAtOTYyYi0xNDUzYzEwMTE4NjUiLCJ1c2VyX2idIjoxfQ.some_long_refresh_token_string",
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjc3OTk3NDkwLCJpYXQiOjE2Nzc5OTcxOTAsImp0aSI6ImRmN2VmYTczLTI1MTktNDUwMy1hYjYwLWU1Yjc0NzE0NWMwNiIsInVzZXJfaWQiOjEsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIn0.some_long_access_token_string",
                    },
                }
            },
        ),
        status.HTTP_400_BAD_REQUEST: ErrorResponses.get_validation_error_response(),
        **ErrorResponses.get_common_error_responses(include_auth=False),
    }

    operation_description = """
        This endpoint allows users to authenticate.
        
        **Permissions:**
        - `AllowAny`: No authentication is required to access this endpoint.

        **Request Body:**
        The request body expects a JSON object containing user email and password, 
        """
    operation_summary = "Authenticate a user"
    method = "post"
    operation_id = "User Login"


class LogoutDocumentationData:
    """
    Documentation data for logout endpoint
    """

    logout_responses = {
        status.HTTP_200_OK: openapi.Response(
            description="User successfully logged out and refresh token invalidated.",
            schema=LogoutResponseSerializer,
            examples={
                "application/json": {
                    "success": True,
                    "message": "Logout successfully processed",
                    "data": None,
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 200,
                    "metadata": {},
                }
            },
        ),
        status.HTTP_400_BAD_REQUEST: ErrorResponses.get_validation_error_response(),
        **ErrorResponses.get_common_error_responses(include_auth=True),
    }

    operation_description = """
        This endpoint allows authenticated users to logout by invalidating their refresh token.
        
        **Authentication Required:**
        - Bearer Token: Valid access token must be provided in the Authorization header.
        
        **Request Body:**
        The request body must contain the refresh token that needs to be invalidated.
        
        **Security:**
        - The refresh token will be blacklisted and cannot be used for future token refresh operations.
        - The user will need to login again to obtain new tokens.
        
        **Note:**
        This endpoint only invalidates the specific refresh token provided. 
        If the user has multiple active sessions, use the logout-all endpoint to invalidate all sessions.
        """

    operation_summary = "Logout user by invalidating refresh token"
    method = "post"
    operation_id = "logout_user"


class LogoutAllDocumentationData:
    """
    Documentation data for logout all sessions endpoint
    """

    operation_description = """
        This endpoint allows authenticated users to logout from ALL active sessions by invalidating 
        all refresh tokens associated with their account.
        
        **Authentication Required:**
        - Bearer Token: Valid access token must be provided in the Authorization header.
        
        **Request Body:**
        No request body is required for this endpoint.
        
        **Security:**
        - All refresh tokens associated with the user's account will be blacklisted.
        - The user will be logged out from all devices and sessions.
        - All existing refresh tokens will become invalid and cannot be used for token refresh operations.
        
        **Use Cases:**
        - When a user suspects their account has been compromised.
        - When a user wants to logout from all devices at once.
        - For security purposes when changing passwords or sensitive account information.
        """

    operation_summary = "Logout user from all active sessions"
    method = "post"
    operation_id = "logout_user_all_sessions"
    logout_all_responses = {
        status.HTTP_200_OK: openapi.Response(
            description="User successfully logged out and refresh token invalidated.",
            schema=LogoutResponseSerializer,
            examples={
                "application/json": {
                    "success": True,
                    "message": "All Logout successfully processed.",
                    "data": None,
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 200,
                    "metadata": {},
                }
            },
        ),
        status.HTTP_400_BAD_REQUEST: ErrorResponses.get_validation_error_response(),
        **ErrorResponses.get_common_error_responses(include_auth=True),
    }
