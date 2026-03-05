from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from ..models import Reservation
from ..exceptions import (
    ReservationDateInvalid,
    ReservationHourInvalid,
    ReservationCustomerLimitExceeded,
    ReservationCannotChangeStatus,
)
from apps.shared.utils.restaurant_information import (
    OPENING_HOUR,
    CLOSING_HOUR,
    MAX_CUSTOMERS_PER_RESERVATION,
)


class ReservationValidationService:
    @classmethod
    def validate_reservation_date(cls, reservation_date: datetime) -> None:
        """
        Validates the reservation date and time constraints.
        """
        now = timezone.now()
        max_date_allowed = now + relativedelta(months=1)

        if reservation_date.replace(second=0, microsecond=0) < now.replace(
            second=0, microsecond=0
        ):
            raise ReservationDateInvalid(
                "Reservations must be made for a future date and time."
            )

        if reservation_date.date() == now.date():
            raise ReservationDateInvalid("Same day reservations are not allowed.")

        if reservation_date > max_date_allowed:
            raise ReservationDateInvalid(
                "Reservations can only be made up to one month in advance."
            )

    @classmethod
    def validate_reservation_hour(cls, reservation_date: datetime) -> None:
        """
        Validates the reservation hour against opening and closing times.
        """
        reservation_hour = reservation_date.hour
        if not (OPENING_HOUR <= reservation_hour < CLOSING_HOUR):
            raise ReservationHourInvalid(
                f"Reservations can only be scheduled between {OPENING_HOUR}:00 and {CLOSING_HOUR-1}:59."
            )

    @classmethod
    def validate_customer_limit(cls, customer_number: int) -> None:
        """
        Validates the number of customers against the maximum allowed.
        """
        if customer_number > MAX_CUSTOMERS_PER_RESERVATION:
            raise ReservationCustomerLimitExceeded(
                f"Reservation can't be for more than {MAX_CUSTOMERS_PER_RESERVATION} customers."
            )

    @classmethod
    def validate_new_reservation_data(cls, reservation: Reservation) -> None:
        """
        Performs all necessary validations for creating a new reservation.
        """
        cls.validate_reservation_date(reservation.reservation_date)
        cls.validate_reservation_hour(reservation.reservation_date)
        cls.validate_customer_limit(reservation.customer_number)

    @classmethod
    def validate_status_transition(
        cls, reservation: Reservation, new_status: str
    ) -> None:
        current_status = reservation.status
        match current_status:
            case "PENDING":
                if new_status not in ["BOOKED", "CANCELLED"]:
                    raise ReservationCannotChangeStatus(
                        f"Pending reservations con only be booked or cancelled"
                    )
            case "BOOKED":
                if new_status not in ["CANCELLED", "NOT_ATTENDED", "ATTENDED"]:
                    raise ReservationCannotChangeStatus(
                        "Booked reservations can't be Pending"
                    )
            case _:
                raise ReservationCannotChangeStatus(
                    "Cancelled/Attended/Not-Attended reservations are not allowed to change"
                )
