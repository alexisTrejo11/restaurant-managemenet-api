from datetime import datetime, timedelta
from django.db import transaction
from ..models import Stock, StockTransaction
from ..exceptions.stock_exceptions import InvalidStockFieldError
from apps.shared.exceptions.custom_exceptions import EntityNotFoundException
from .stock_service import StockService


class StockTransactionService:
    """
    Service for specific operations with stock transactions.
    """

    @classmethod
    def get_transaction(cls, transaction_id: int) -> StockTransaction:
        try:
            return StockTransaction.objects.get(id=transaction_id)
        except:
            raise EntityNotFoundException("Transaction", transaction_id)

    @classmethod
    def process_transaction(cls, validated_data: dict) -> StockTransaction:
        """
        Processes a stock transaction (in/out), creating a new transaction record
        and updating the corresponding stock quantity.

        Args:
            validated_data (dict): Validated data from the serializer,
                                   including 'stock', 'ingredient_quantity', 'transaction_type'.

        Returns:
            StockTransaction: The newly created transaction.
        Raises:
            InvalidStockFieldError: If the transaction is invalid (e.g., insufficient stock).
        """
        with transaction.atomic():
            stock = validated_data["stock"]
            quantity = validated_data["ingredient_quantity"]
            transaction_type = validated_data["transaction_type"]

            cls._validate_transaction_logic(stock, quantity, transaction_type)
            cls._adjust_stock_quantity(stock, quantity, transaction_type)

            return StockTransaction.objects.create(stock=stock, **validated_data)

    @classmethod
    def update_transaction(
        cls, existing_transaction: StockTransaction, validated_data: dict
    ) -> StockTransaction:
        """
        Updates an existing stock transaction and adjusts the corresponding stock quantity.
        This involves reverting the old transaction's effect and applying the new one.

        Args:
            existing_transaction (StockTransaction): The transaction instance to be updated.
            validated_data (dict): Validated data for the update, which may include
                                   'ingredient_quantity' and 'transaction_type'.

        Returns:
            StockTransaction: The updated transaction.
        Raises:
            InvalidStockFieldError: If the updated transaction would result in an invalid stock state.
        """
        with transaction.atomic():
            stock = existing_transaction.stock

            # Revert the effect of the OLD transaction
            cls._adjust_stock_quantity(
                stock,
                existing_transaction.ingredient_quantity,
                cls._get_reverse_transaction_type(
                    existing_transaction.transaction_type
                ),
            )

            new_quantity = validated_data.get(
                "ingredient_quantity", existing_transaction.ingredient_quantity
            )
            new_transaction_type = validated_data.get(
                "transaction_type", existing_transaction.transaction_type
            )

            cls._validate_transaction_logic(stock, new_quantity, new_transaction_type)
            cls._adjust_stock_quantity(stock, new_quantity, new_transaction_type)

            existing_transaction.ingredient_quantity = new_quantity
            existing_transaction.transaction_type = new_transaction_type
            existing_transaction.save()

            return existing_transaction

    @classmethod
    def delete_transaction(cls, transaction_to_delete: StockTransaction) -> None:
        """
        Deletes a stock transaction and correctly reverts its effect on the total stock.

        Args:
            transaction_to_delete (StockTransaction): The transaction instance to be deleted.
        Raises:
            InvalidStockFieldError: If reverting the transaction would result in an invalid stock state.
        """
        with transaction.atomic():
            stock = transaction_to_delete.stock
            reverse_type = cls._get_reverse_transaction_type(
                transaction_to_delete.transaction_type
            )

            cls._validate_transaction_logic(
                stock, transaction_to_delete.ingredient_quantity, reverse_type
            )
            cls._adjust_stock_quantity(
                stock, transaction_to_delete.ingredient_quantity, reverse_type
            )

            transaction_to_delete.delete()

    @classmethod
    def _adjust_stock_quantity(
        cls, stock: Stock, quantity: int, transaction_type: str
    ) -> None:
        """
        Adjusts the stock quantity based on transaction type.
        """
        if transaction_type == "IN":
            stock.total_stock += quantity
        else:
            stock.total_stock -= quantity
        stock.save()

    @classmethod
    def _get_reverse_transaction_type(cls, transaction_type: str) -> str:
        """
        Returns the reverse transaction type for reverting operations.
        """
        return "OUT" if transaction_type == "IN" else "IN"

    @classmethod
    def _validate_transaction_logic(
        cls, stock: Stock, quantity: int, transaction_type: str
    ) -> None:
        """
        Performs comprehensive validation for a potential stock transaction.
        This includes checking for sufficient stock for 'OUT' and not exceeding limits for 'IN'.
        """
        if quantity <= 0:
            raise InvalidStockFieldError(
                "Transaction quantity must be greater than zero."
            )

        if transaction_type not in ("IN", "OUT"):
            raise InvalidStockFieldError(
                f"Invalid transaction type: {transaction_type}. Must be 'IN' or 'OUT'."
            )

        if transaction_type == "OUT":
            if stock.total_stock < quantity:
                raise InvalidStockFieldError(
                    "Quantity to withdraw exceeds available stock."
                )
        else:  # IN
            if stock.total_stock + quantity > stock.optimal_stock_quantity:
                raise InvalidStockFieldError(
                    f"Quantity to add exceeds the global stock limit of {StockService.MAX_STOCK_LIMIT}."
                )
