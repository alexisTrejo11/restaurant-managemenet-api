from ..models import Order, OrderItem
from ..exceptions import (
    OrderNotFound,
    TableNotAvailableForOrder,
    OrderStatusInvalid,
    OrderAlreadyCompletedOrCancelled,
    OrderDeletionForbidden,
    OrderEmptyCanNotBeComplete,
)
from django.db import transaction
import logging
from apps.tables.models import Table

logger = logging.getLogger(__name__)


class OrderService:
    @classmethod
    def get_order(cls, order_id: int, active=False) -> Order:
        """Retrieves an order by its ID, raising an error if not found."""
        try:
            if active:
                order = Order.objects.get(id=order_id, status="IN_PROGRESS")
            else:
                order = Order.objects.get(id=order_id)
            return order
        except Order.DoesNotExist:
            logger.error(f"Order with ID {order_id} does not exist.")
            raise OrderNotFound(f"Order with ID {order_id} was not found.")

    @classmethod
    def start_order(cls, validated_data: dict) -> Order:
        """
        Creates a new order instance after performing all necessary validations.
        Ensures the table is available and sets the initial status.
        """
        table = validated_data.get("table")

        if not table.is_available:
            logger.warning(f"Attempted to start order on unavailable table: {table.id}")
            raise TableNotAvailableForOrder(
                f"Table {table.number} is currently not available."
            )

        status_value = validated_data.get("status")
        if status_value != "IN_PROGRESS":
            logger.warning(
                f"Attempted to start order with status '{status_value}'. Must be 'IN_PROGRESS'."
            )
            raise OrderStatusInvalid(
                "New orders must be started with 'IN_PROGRESS' status."
            )

        try:
            with transaction.atomic():
                order = Order.objects.create(**validated_data)
                cls._take_table(order)
                logger.info(
                    f"Order {order.id} started successfully for table {table.id}."
                )
                return order
        except Exception as e:
            logger.exception(
                f"Unexpected error creating order with data {validated_data}."
            )
            raise

    # TODO: Refacotr
    @classmethod
    def update_order(
        cls, order: Order, new_status: str = None, new_table=None
    ) -> Order:
        """
        Updates an existing order instance after performing necessary validations.
        Allows updating status or reassigning table.
        """
        cls._validate_order_modifiability(order)

        if new_status and new_status != order.status:
            if new_status == "COMPLETED":
                return cls.complete_order(order)
            elif new_status == "CANCELLED":
                return cls.cancel_order(order)
            else:
                order.status = new_status
                logger.info(f"Order {order.id} status updated to {new_status}.")

        if new_table and new_table.id != order.table.id:
            cls._update_order_table(order, new_table)
            logger.info(f"Order {order.id} moved to table {new_table.id}.")

        try:
            with transaction.atomic():
                order.save()
                return order
        except Exception as e:
            logger.exception(f"Unexpected error updating order ID {order.id}.")
            raise

    @classmethod
    def delete_order(cls, order: Order):
        """
        Deletes an order instance after performing all necessary validations.
        Only allows deletion of orders that are in a modifiable state.
        """
        cls._validate_order_modifiability(order, for_deletion=True)
        try:
            with transaction.atomic():
                order_id = order.id
                order.delete()
                logger.info(f"Order {order_id} deleted successfully.")
        except Exception as e:
            logger.exception(f"Unexpected error deleting order ID {order.id}.")
            raise

    @classmethod
    def update_order_status(cls, order: Order, new_status: str):
        """High-level method to handle status transitions."""
        cls._validate_order_modifiability(order)

        if new_status == "COMPLETED":
            return cls.complete_order(order)
        elif new_status == "CANCELLED":
            return cls.cancel_order(order)
        elif new_status != order.status:
            order.status = new_status
            order.save()
            logger.info(f"Order {order.id} status manually updated to {new_status}.")
            return order
        return order

    @classmethod
    def complete_order(cls, order: Order):
        """Marks an order as completed and frees up its table."""
        cls._validate_order_modifiability(order)
        cls._validate_no_empty_order(order)

        if order.status == "COMPLETED":
            logger.info(f"Order {order.id} already completed.")
            return order

        try:
            with transaction.atomic():
                order.set_as_complete()
                order.save()
                cls._clear_table(order)
                logger.info(
                    f"Order {order.id} completed and table {order.table.id} cleared."
                )
                return order
        except Exception as e:
            logger.exception(f"Error completing order {order.id}.")
            raise

    @classmethod
    def cancel_order(cls, order: Order):
        """Marks an order as cancelled and frees up its table."""
        cls._validate_order_modifiability(order)
        if order.status == "CANCELLED":
            logger.info(f"Order {order.id} already cancelled.")
            return order

        try:
            with transaction.atomic():
                order.set_as_cancelled()
                order.save()
                cls._clear_table(order)
                logger.info(
                    f"Order {order.id} cancelled and table {order.table.id} cleared."
                )
                return order
        except Exception as e:
            logger.exception(f"Error cancelling order {order.id}.")
            raise

    @classmethod
    def _update_order_table(cls, order: Order, new_table: Table):
        """Internal: Handles changing an order's table."""
        if not new_table.is_available:
            logger.warning(
                f"Attempted to move order {order.id} to unavailable table {new_table.id}."
            )
            raise TableNotAvailableForOrder(
                f"Table {new_table.number} is not available for transfer."
            )

        with transaction.atomic():
            cls._clear_table(order)
            order.table = new_table
            order.save()
            cls._take_table(order)

        logger.info(
            f"Order {order.id} successfully moved from table {order.table.id} to {new_table.id}."
        )

    @classmethod
    def _validate_order_modifiability(cls, order: Order, for_deletion: bool = False):
        """
        Internal: Validates if an order is in a state that allows modification or deletion.
        """
        if order.status == "COMPLETED" or order.status == "CANCELLED":
            logger.warning(
                f"Attempted to modify/delete finalized order {order.id} (status: {order.status})."
            )
            raise OrderAlreadyCompletedOrCancelled(
                f"Order {order.id} is already {order.status} and cannot be modified."
            )

        if for_deletion and order.status not in ["IN_PROGRESS", "CANCELLED"]:
            raise OrderDeletionForbidden(
                "Onyl In Progress or Cancelled Order cna be deleted"
            )

    @classmethod
    def _validate_order_modifiability(cls, order: Order, for_deletion: bool = False):
        """
        Internal: Validates if an order is in a state that allows modification or deletion.
        """
        if order.status == "COMPLETED" or order.status == "CANCELLED":
            logger.warning(
                f"Attempted to modify/delete finalized order {order.id} (status: {order.status})."
            )
            raise OrderAlreadyCompletedOrCancelled(
                f"Order {order.id} is already {order.status} and cannot be modified."
            )

        if for_deletion and order.status not in ["IN_PROGRESS", "CANCELLED"]:
            raise OrderDeletionForbidden(
                "Onyl In Progress or Cancelled Order cna be deleted"
            )

    @classmethod
    def _clear_table(cls, order: Order):
        """Internal: Marks the table associated with an order as available."""
        table = order.table
        if table:
            table.is_available = True
            table.save()
            logger.debug(f"Table {table.id} cleared for order {order.id}.")

    @classmethod
    def _take_table(cls, order: Order):
        """Internal: Marks the table associated with an order as unavailable."""
        table = order.table
        if table:
            table.is_available = False
            table.save()
            logger.debug(f"Table {table.id} taken for order {order.id}.")

    @classmethod
    def _validate_no_empty_order(cls, order: Order):
        if OrderItem.objects.filter(order=order).count() == 0:
            raise OrderEmptyCanNotBeComplete("Empty Orders can't be completed")
