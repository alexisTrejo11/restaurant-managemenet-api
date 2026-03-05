from rest_framework.exceptions import APIException
from rest_framework import status

class UserError(APIException):
    """Base exception for all user-related API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A user-related error occurred."
    default_code = "user_error"

class InvalidEmailError(UserError):
    """Raised when the email format is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The email address provided is invalid."
    default_code = "invalid_email"

class MissingEmailError(UserError):
    """Raised when the email is required but missing."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Email address is required."
    default_code = "missing_email"

class InvalidPasswordError(UserError):
    """Raised when the password does not meet complexity requirements."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The password does not meet the complexity requirements."
    default_code = "invalid_password"

class MissingPasswordError(UserError):
    """Raised when the password is required but missing."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Password is required."
    default_code = "missing_password"

class InvalidPhoneNumberError(UserError):
    """Raised when the phone number format is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The phone number format is invalid."
    default_code = "invalid_phone_number"

class UserUpdateError(UserError):
    """Raised when user update validation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Failed to update user due to validation errors."
    default_code = "user_update_failed"