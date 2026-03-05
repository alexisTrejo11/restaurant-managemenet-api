from rest_framework.exceptions import APIException
from rest_framework import status

class DishException(APIException):
    """Base exception for all menu item-related API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A menu item-related error occurred."
    default_code = "menu_item_error"

class InvalidDishCategory(DishException):
    """Raised when the provided menu item category is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The provided menu item category is invalid."
    default_code = "invalid_menu_item_category"

class InvalidDishPrice(DishException):
    """Raised when the menu item price does not meet validation rules."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The menu item price is invalid."
    default_code = "invalid_menu_item_price"

class DuplicateDishName(DishException):
    """Raised when a menu item with the same name already exists."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "A menu item with this name already exists."
    default_code = "duplicate_menu_item_name"

class InvalidDishStatus(DishException):
    """Raised when the provided menu item status is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The provided menu item status is invalid."
    default_code = "invalid_menu_item_status"

class DishNotFound(DishException):
    """Raised when a menu item record is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Menu item not found."
    default_code = "menu_item_not_found"