from rest_framework.exceptions import APIException
from rest_framework import status

class ReservationException(APIException):
    """Base exception for all reservation-related API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A reservation-related error occurred."
    default_code = "RESERVATION_ERROR"

class ReservationDateInvalid(ReservationException):
    """Raised when the reservation date is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The provided reservation date is invalid."
    default_code = "RESERVATION_DATE_INVALID"

class TableNotAvailableForReservation(ReservationException):
    """Raised when no suitable tables are available for the reservation."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "No suitable tables are available for the requested reservation details."
    default_code = "NOT_SUITABLE_TABLES_AVAILABLE"

class ReservationHourInvalid(ReservationException):
    """Raised when the reservation hour is invalid."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The provided reservation hour is invalid or outside operating hours."
    default_code = "RESERVATION_HOUR_INVALID"

class ReservationCustomerLimitExceeded(ReservationException):
    """Raised when the number of customers for a reservation exceeds the allowed limit."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The number of customers for the reservation exceeds the allowed limit."
    default_code = "RESERVATION_CUSTOMER_LIMIT_EXCEEDED"

class ReservationAlreadyCancelled(ReservationException):
    """Raised when an operation is attempted on an already cancelled reservation."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This reservation has already been cancelled and cannot be modified."
    default_code = "RESERVATION_ALREADY_CANCELLED"

class ReservationCannotChangeStatus(ReservationException):
    """Raised when a reservation's status cannot be changed to the requested state."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "The reservation status cannot be changed to the requested state."
    default_code = "RESERVATION_CANNOT_CHANGE_STATUS"

class ReservationNotFound(ReservationException):
    """Raised when a reservation record is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "The requested reservation was not found."
    default_code = "RESERVATION_NOT_FOUND"