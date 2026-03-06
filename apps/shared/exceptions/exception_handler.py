import logging
from datetime import datetime
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import APIException, ValidationError
from django.core.exceptions import PermissionDenied
from django.http import Http404
from apps.shared.response import (
    ForbiddenErrorResponseSerializer,
    NotFoundErrorResponseSerializer,
    ValidationErrorResponseSerializer,
    UnauthorizedErrorResponseSerializer,
    ServerErrorResponseSerializer,
)
from typing import Dict, Any, Optional, Union
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Enhanced unified exception handler with:
    - Detailed error logging
    - Special handling for common exception types
    - Consistent error response structure
    - Request context in logs
    - Type hints for better maintainability

    Args:
        exc: The exception instance
        context: DRF context containing request, view, args, kwargs

    Returns:
        Response: Consistent error response
    """
    request = context.get("request")
    view = context.get("view")

    logger.error(
        f"Exception occurred: {str(exc)}\n"
        f"Type: {exc.__class__.__name__}\n"
        f"Request: {request.method} {request.path if request else 'No request'}\n"
        f"View: {view.__class__.__name__ if view else 'No view'}",
        exc_info=True,
    )

    response = drf_exception_handler(exc, context)

    if isinstance(exc, (InvalidToken, TokenError)):
        return handle_jwt_exception(exc)

    if isinstance(exc, ValueError):
        return handle_value_error(exc)

    if isinstance(exc, Http404):
        return Response(
            data={
                "data": {"type": "NotFound"},
                "timestamp": datetime.now().isoformat() + "Z",
                "success": False,
                "status_code": 404,
                "message": str(exc) or "Resource not found",
                "metadata": {},
            },
            status=404,
        )

    if isinstance(exc, PermissionDenied):
        return Response(data=ForbiddenErrorResponseSerializer(), status=403)

    if isinstance(exc, ValidationError):
        return handle_validation_error(exc)

    if response is not None:
        return handle_drf_response(exc, response)

    if isinstance(exc, APIException):
        return handle_api_exception(exc)

    return handle_unexpected_error(exc)


def handle_validation_error(exc: ValidationError) -> Response:
    """Special handling for DRF validation errors"""
    error_data = {
        "type": "ValidationError",
        "code": "invalid",
        "fields": exc.detail if isinstance(exc.detail, dict) else None,
    }
    return Response(
        data={
            "data": error_data,
            "timestamp": datetime.now().isoformat() + "Z",
            "success": False,
            "status_code": 400,
            "message": "Validation failed" if not str(exc) else str(exc),
            "metadata": {},
        },
        status=400,
    )


def handle_drf_response(exc: Exception, response) -> Response:
    """Handle responses from DRF's default exception handler"""
    error_data = {
        "type": exc.__class__.__name__,
        "code": getattr(exc, "default_code", None),
        "details": normalize_error_details(response.data),
    }
    return Response(
        data={
            "data": error_data,
            "timestamp": datetime.now().isoformat() + "Z",
            "success": False,
            "status_code": response.status_code,
            "message": get_error_message(exc),
            "metadata": {},
        },
        status=response.status_code,
    )


def handle_api_exception(exc: APIException) -> Response:
    """Handle custom APIException-based exceptions"""
    error_data = {
        "type": exc.__class__.__name__,
        "code": getattr(exc, "default_code", None),
        "details": normalize_error_details(getattr(exc, "detail", None)),
    }
    status_code = getattr(exc, "status_code", 400)
    return Response(
        data={
            "data": error_data,
            "timestamp": datetime.now().isoformat() + "Z",
            "success": False,
            "status_code": status_code,
            "message": get_error_message(exc),
            "metadata": {},
        },
        status=status_code,
    )


def handle_unexpected_error(exc: Exception) -> Response:
    """Fallback handler for unexpected exceptions"""
    logger.critical("Unhandled exception occurred", exc_info=True, stack_info=True)
    return Response(
        data={
            "data": {"type": "InternalServerError"},
            "timestamp": datetime.now().isoformat() + "Z",
            "success": False,
            "status_code": 500,
            "message": "An unexpected error occurred",
            "metadata": {},
        },
        status=500,
    )


def normalize_error_details(details: Any) -> Optional[Dict]:
    """Convert various error detail formats to consistent dictionary"""
    if details is None:
        return None
    if isinstance(details, dict):
        return details
    if isinstance(details, list):
        return {"non_field_errors": details}
    return {"message": str(details)}


def get_error_message(exc: Exception) -> str:
    """Extract appropriate error message from exception, handling DRF specifics."""
    if isinstance(exc, APIException):
        if hasattr(exc, "detail"):
            if isinstance(exc.detail, dict):
                return "Validation failed or complex error details"
            return str(exc.detail)

    return str(exc) if str(exc) else "Request failed"


def handle_jwt_exception(exc: Union[InvalidToken, TokenError]) -> Response:
    """Special handling for JWT token related exceptions"""
    error_data = {
        "type": exc.__class__.__name__,
        "code": "token_error",
        "details": get_jwt_error_details(exc),
    }

    status_code = 401 if isinstance(exc, InvalidToken) else 400

    return Response(
        data={
            "data": error_data,
            "timestamp": datetime.now().isoformat() + "Z",
            "success": False,
            "status_code": status_code,
            "message": get_jwt_error_message(exc),
            "metadata": {},
        },
        status=status_code,
    )


def get_jwt_error_details(exc: Union[InvalidToken, TokenError]) -> Dict:
    """Extract details from JWT exceptions"""
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, dict):
            return exc.detail
        return {"message": str(exc.detail)}
    return {"message": str(exc)}


def get_jwt_error_message(exc: Union[InvalidToken, TokenError]) -> str:
    """Extract user-friendly message from JWT exceptions"""
    if hasattr(exc, "detail"):
        if isinstance(exc.detail, dict):
            if "messages" in exc.detail and exc.detail["messages"]:
                first_msg = exc.detail["messages"][0]
                if isinstance(first_msg, dict) and "message" in first_msg:
                    return first_msg["message"]
            return exc.detail.get("detail", str(exc))
        return str(exc.detail)
    return "Authentication token error"


def handle_value_error(exc: ValueError) -> Response:
    """Special handling for ValueError exceptions"""
    return Response(
        data={
            "data": {
                "type": "ValueError",
                "code": "invalid_value",
                "details": str(exc),
            },
            "timestamp": datetime.now().isoformat() + "Z",
            "success": False,
            "status_code": 400,
            "message": "Invalid data provided: " + str(exc),
            "metadata": {},
        },
        status=400,
    )
