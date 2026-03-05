from rest_framework.exceptions import APIException
from rest_framework import status

class TableException(APIException):
    """Base exception for all table-related API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A table-related error occurred."
    default_code = "table_error"

class TableCapacityExceeded(TableException):
    """
    Exception raised when the provided table capacity exceeds the maximum allowed.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The provided table capacity is out of the allowed range."
    default_code = "table_capacity_exceeded"

class RestaurantCapacityFull(TableException):
    """
    Exception raised when trying to create a new table but the restaurant
    has already reached its maximum allowed number of tables.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The restaurant has reached its maximum table capacity. Cannot add more tables."
    default_code = "restaurant_capacity_full"

class TableNumberAlreadyExists(TableException):
    """
    Exception raised when attempting to create or update a table with a number
    that is already assigned to another table.
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The table number provided is already in use by another table."
    default_code = "table_number_already_exists"

class TableInUse(TableException):
    """
    Exception raised when attempting to delete a table that is currently in use
    (e.g., has active reservations or orders).
    """
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Cannot perform this operation as the table is currently in use or has active dependencies."
    default_code = "table_in_use"


class TableNotFound(TableException):
    """Raised when a specific table record is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "The specified table was not found."
    default_code = "table_not_found"