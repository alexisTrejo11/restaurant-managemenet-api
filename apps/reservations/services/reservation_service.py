from django.db import transaction
from apps.tables.models import Table
from .reservation_validation_service import (
    ReservationValidationService as validatonService,
)
from apps.tables.services.table_service import TableService
from typing import List, Optional
from django.utils.timezone import timedelta
from ..models import Reservation
from ..exceptions import TableNotAvailableForReservation, ReservationNotFound


class ReservationService:
    @classmethod
    def get_reservation_by_id(cls, reservation_id):
        try:
            return Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            raise ReservationNotFound("Reservation", reservation_id)

    @classmethod
    def get_reservation_by_date_range(cls, start_date, end_date):
        return Reservation.objects.filter(
            reservation_date__gte=start_date, reservation_date__lte=end_date
        )

    @classmethod
    def create_reservation(cls, validated_data: dict, is_admin=True) -> Reservation:
        reservation = Reservation.from_dict(validated_data)
        validatonService.validate_new_reservation_data(reservation)

        cls._assign_table(reservation)
        cls._assing_status(is_admin, reservation)

        with transaction.atomic():
            reservation.save()
            return reservation

    # TODO:
    @classmethod
    def update_reservation(
        cls, reservation: Reservation, validated_data: dict
    ) -> Reservation:
        for attr, value in validated_data.items():
            setattr(reservation, attr, value)

        if "reservation_date" in validated_data:
            validatonService.validate_reservation_date(reservation.reservation_date)
            validatonService.validate_reservation_hour(reservation.reservation_date)
        if "customer_number" in validated_data:
            validatonService.validate_customer_limit(reservation.customer_number)

        with transaction.atomic():
            reservation.save()
            return reservation

    @classmethod
    def update_status_reservation(cls, reservation_id, new_status):
        reservation = cls.get_reservation_by_id(reservation_id)
        validatonService.validate_status_transition(reservation, new_status)

        with transaction.atomic():
            reservation.update_status(new_status)
            reservation.save()
            return reservation

    @classmethod
    def is_status_valid(cls, new_status) -> bool:
        valid_statuses = [choice[0] for choice in Reservation.STATUS_CHOICES]
        return new_status in valid_statuses

    @classmethod
    def _assign_table(cls, reservation: Reservation) -> None:
        suitable_tables = TableService.find_suitable_tables_to_order(
            reservation.customer_number
        )
        if len(suitable_tables) == 0:
            raise TableNotAvailableForReservation()

        assigned_table = cls._select_table_with_no_reservation(
            suitable_tables, reservation
        )
        if not assigned_table:
            raise TableNotAvailableForReservation()

        reservation.table = assigned_table

    @classmethod
    def _assing_status(cls, is_admin: bool, reservation: Reservation):
        if is_admin:
            reservation.set_as_booked()
        else:
            reservation.set_as_pending()
            ##EmailService.send_reservation_confirmation(reservation)

    @classmethod
    def _select_table_with_no_reservation(
        cls, suitable_tables: List[Table], reservation: Reservation
    ) -> Table:
        selected_table = None

        for table in suitable_tables:
            if not cls._is_another_reservation_with_same_table(
                table.number, reservation.reservation_date
            ):
                selected_table = table
                break

        return selected_table

    @classmethod
    def _is_another_reservation_with_same_table(
        cls, table_number, reservation_date
    ) -> Optional[Reservation]:
        start_time = reservation_date - timedelta(hours=2)
        end_time = reservation_date + timedelta(hours=3)

        return Reservation.objects.filter(
            table__number=table_number, reservation_date__range=(start_time, end_time)
        ).exists()
