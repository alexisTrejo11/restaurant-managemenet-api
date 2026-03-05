from rest_framework.exceptions import APIException
from rest_framework import status

class StockException(APIException):
    """Base exception for all stock-related API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A stock-related error occurred."
    default_code = "stock_error"

class StockNotFoundError(StockException):
    """Raised when a stock record is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Stock record not found."
    default_code = "stock_not_found"

class DuplicateStockError(StockException):
    """Raised when a stock record for an ingredient already exists."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "A stock record for this ingredient already exists."
    default_code = "duplicate_stock"

class InvalidTransactionError(StockException):
    """Raised when a stock transaction is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The provided stock transaction is invalid."
    default_code = "invalid_transaction"

class InsufficientStockError(StockException):
    """Raised when there's not enough stock for an operation."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY 
    default_detail = "Insufficient stock for this operation."
    default_code = "insufficient_stock"

class InvalidStockFieldError(StockException):
    """Raised when a stock property has an invalid value."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "One or more stock fields contain invalid values."
    default_code = "invalid_stock_field"



class StockTransactionException(APIException):
    """Base exception for all stock transaction API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A stock transaction-related error occurred."
    default_code = "stock_transaction_error"

class StockTransactionNotFound(StockTransactionException):
    """Raised when a stock transaction record is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Stock transaction not found."
    default_code = "stock_transaction_not_found"