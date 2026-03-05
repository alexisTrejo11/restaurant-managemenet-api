from rest_framework.exceptions import APIException
from rest_framework import status

class OrderException(APIException):
    """Base exception for all order-related API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An order-related error occurred."
    default_code = "order_error"

class OrderNotFound(OrderException):
    """Raised when an order is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Order not found."
    default_code = "order_not_found"

class TableNotAvailableForOrder(OrderException):
    """Raised when a table is not available for a new order."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The selected table is currently not available for orders."
    default_code = "table_not_available_for_order"

class OrderStatusInvalid(OrderException):
    """Raised when an order status is invalid for the operation."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid order status for this operation."
    default_code = "order_status_invalid"

class OrderAlreadyCompletedOrCancelled(OrderException):
    """Raised when trying to modify an order that is already completed or cancelled."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This order is already completed or cancelled and cannot be modified."
    default_code = "order_already_finalized"

class OrderDeletionForbidden(OrderException):
    """Raised when an order cannot be deleted due to its status or other rules."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "This order cannot be deleted in its current state."
    default_code = "order_deletion_forbidden"


class OrderEmptyCanNotBeComplete(OrderException):
    """Raised when an order has no items and can't be completed only cancelled"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This order cannot be completed"
    default_code = "order_empty_can_not_be_complete"
