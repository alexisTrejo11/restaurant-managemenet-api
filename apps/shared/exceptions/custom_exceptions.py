from rest_framework.exceptions import APIException


class EntityNotFoundException(APIException):
    """
    Exception raised when an entity is not found in the database.
    """
    status_code = 404
    default_detail = "Entity Not Found"
    default_code = "entity_not_found"


class InvalidFilterException(APIException):
    """
    Exception raised when filter parameters are invalid.
    """
    def __init__(self, filter_name: str):
        message = f"Invalid filter: {filter_name}."
        super().__init__(message=message, status_code=400)


class BusinessRuleViolationException(APIException):
    """
    Exception raised when a business rule is violated.
    """
    status_code = 400
    default_detail = "BusinessRuleViolation"
    default_code = "stock_error"


class DomainException(APIException):
    """
    Exception raised when a domain rule is violated.
    """
    def __init__(self, rule_description: str):
        message = f"Domain rule violation: {rule_description}."
        super().__init__(message=message, status_code=409)