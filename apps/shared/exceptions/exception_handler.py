import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import APIException, ValidationError
from django.core.exceptions import PermissionDenied
from django.http import Http404
from apps.shared.response import ResponseWrapper
from typing import Dict, Any, Optional, Union
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


logger = logging.getLogger(__name__)


def custom_exception_handler(
    exc: Exception, context: Dict[str, Any]
) -> ResponseWrapper:
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
        ResponseWrapper: Consistent error response
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
        return ResponseWrapper.failure(
            status_code=404,
            data={"type": "NotFound"},
            message=str(exc) or "Resource not found",
        )

    if isinstance(exc, PermissionDenied):
        return ResponseWrapper.forbidden(
            data={"type": "PermissionDenied"},
            message=str(exc) or "You don't have permission to perform this action",
        )

    if isinstance(exc, ValidationError):
        return handle_validation_error(exc)

    if response is not None:
        return handle_drf_response(exc, response)

    if isinstance(exc, APIException):
        return handle_api_exception(exc)

    return handle_unexpected_error(exc)


def handle_validation_error(exc: ValidationError) -> ResponseWrapper:
    """Special handling for DRF validation errors"""
    error_data = {
        "type": "ValidationError",
        "code": "invalid",
        "fields": exc.detail if isinstance(exc.detail, dict) else None,
    }
    return ResponseWrapper.failure(
        data=error_data,
        message="Validation failed" if not str(exc) else str(exc),
        status_code=400,
    )


def handle_drf_response(exc: Exception, response) -> ResponseWrapper:
    """Handle responses from DRF's default exception handler"""
    error_data = {
        "type": exc.__class__.__name__,
        "code": getattr(exc, "default_code", None),
        "details": normalize_error_details(response.data),
    }
    return ResponseWrapper.failure(
        data=error_data,
        message=get_error_message(exc),
        status_code=response.status_code,
    )


def handle_api_exception(exc: APIException) -> ResponseWrapper:
    """Handle custom APIException-based exceptions"""
    error_data = {
        "type": exc.__class__.__name__,
        "code": getattr(exc, "default_code", None),
        "details": normalize_error_details(getattr(exc, "detail", None)),
    }
    return ResponseWrapper.failure(
        data=error_data,
        message=get_error_message(exc),
        status_code=getattr(exc, "status_code", 400),
    )


def handle_unexpected_error(exc: Exception) -> ResponseWrapper:
    """Fallback handler for unexpected exceptions"""
    logger.critical("Unhandled exception occurred", exc_info=True, stack_info=True)
    return ResponseWrapper.internal_server_error(
        data={"type": "InternalServerError"}, message="An unexpected error occurred"
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


def handle_jwt_exception(exc: Union[InvalidToken, TokenError]) -> ResponseWrapper:
    """Special handling for JWT token related exceptions"""
    error_data = {
        "type": exc.__class__.__name__,
        "code": "token_error",
        "details": get_jwt_error_details(exc),
    }

    status_code = 401 if isinstance(exc, InvalidToken) else 400

    return ResponseWrapper.failure(
        data=error_data, message=get_jwt_error_message(exc), status_code=status_code
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


def handle_value_error(exc: ValueError) -> ResponseWrapper:
    """Special handling for ValueError exceptions"""
    return ResponseWrapper.failure(
        status_code=400,
        data={"type": "ValueError", "code": "invalid_value", "details": str(exc)},
        message="Invalid data provided: " + str(exc),
    )
