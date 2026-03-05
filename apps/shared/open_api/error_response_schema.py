from rest_framework import status
from drf_yasg import openapi
from ..response.api_response_serializers import *

class ErrorResponses:
    """
    Centralized authentication error responses for reuse across endpoints
    """
    @staticmethod
    def get_not_found_response():
        return openapi.Response(
            description="Not Found - The requested resource was not found.",
            schema=NotFoundErrorResponseSerializer,
            examples={
                "application/json": {
                    "success": False,
                    "message": "The requested resource was not found.",
                    "data": None,
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 404,
                    "metadata": {}
                }
            }
        )

    @staticmethod
    def get_unauthorized_response():
        return openapi.Response(
            description="Unauthorized - Authentication credentials were not provided or are invalid.",
            schema=UnauthorizedErrorResponseSerializer,
            examples={
                "application/json": {
                    "success": False,
                    "message": "Authentication credentials were not provided.",
                    "data": None,
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 401,
                    "metadata": {}
                }
            }
        )
    
    @staticmethod
    def get_forbidden_response():
        return openapi.Response(
            description="Forbidden - You do not have permission to perform this action.",
            schema=ForbiddenErrorResponseSerializer,
            examples={
                "application/json": {
                    "success": False,
                    "message": "You do not have permission to perform this action.",
                    "data": None,
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 403,
                    "metadata": {}
                }
            }
        )
    
    @staticmethod
    def get_validation_error_response():
        return openapi.Response(
            description="Bad Request - Invalid input data or validation errors.",
            schema=ValidationErrorResponseSerializer,
            examples={
                "application/json": {
                    "success": False,
                    "message": "Validation Error",
                    "data": {
                        "field_1": ["This field is required."],
                        "field_2": ["This field may not be blank."]
                    },
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 400,
                    "metadata": {}
                }
            }
        )
    
    @staticmethod
    def get_server_error_response():
        return openapi.Response(
            description="Internal Server Error - An unexpected error occurred.",
            schema=ServerErrorResponseSerializer,
            examples={
                "application/json": {
                    "success": False,
                    "message": "An unexpected error occurred.",
                    "data": None,
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 500,
                    "metadata": {}
                }
            }
        )

    @staticmethod
    def get_common_error_responses(include_auth=True):
        """
        Returns a dictionary of common error responses that can be merged with endpoint-specific responses
        """
        if include_auth:
            return {
                status.HTTP_401_UNAUTHORIZED: ErrorResponses.get_unauthorized_response(),
                status.HTTP_403_FORBIDDEN: ErrorResponses.get_forbidden_response(),
                status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorResponses.get_server_error_response(),
            }
        else:
            return { 
                status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorResponses.get_server_error_response(),
            }


    @staticmethod
    def get_success_operation():
        return openapi.Response(
            description="Success Operation",
            schema=ForbiddenErrorResponseSerializer,
            examples={
                "application/json": {
                    "success": True,
                    "message": "",
                    "data": "null",
                    "timestamp": "2025-05-28T10:30:00Z",
                    "status_code": 200,
                    "metadata": {}
                }
            }
        )