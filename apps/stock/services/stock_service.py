from datetime import datetime, timedelta
from django.db import transaction
from ..models import Stock, StockTransaction, StockItem
from ..exceptions.stock_exceptions import InvalidStockFieldError
import logging


logger = logging.getLogger(__name__)

class StockService:
    """
    Service for handling inventory business logic.
    """
    MAX_STOCK_LIMIT = 1000
    MIN_STOCK_LIMIT = 0
    
    @staticmethod
    def validate_stock_quantity(total_stock: int, optimal_stock: int) -> None:
        """Validate the stock quantities"""
        if not (StockService.MIN_STOCK_LIMIT <= total_stock <= StockService.MAX_STOCK_LIMIT):
            raise InvalidStockFieldError(f"The total stock must be within the range ({StockService.MIN_STOCK_LIMIT}, {StockService.MAX_STOCK_LIMIT})")
        if not (StockService.MIN_STOCK_LIMIT <= optimal_stock <= StockService.MAX_STOCK_LIMIT):
            raise InvalidStockFieldError(f"The optimal stock must be within the range ({StockService.MIN_STOCK_LIMIT}, {StockService.MAX_STOCK_LIMIT})")

    @classmethod
    def create_stock(cls, validated_data: dict) -> Stock:
        """Creates a new stock record"""
        item = validated_data.get('item') 
        optimal_stock_quantity = validated_data.get('optimal_stock_quantity') 
        initial_stock = validated_data.get('total_stock', 0) 
        
        cls.validate_stock_quantity(initial_stock, optimal_stock_quantity)
        cls._validate_not_duplicated_stock(item)
        return Stock.objects.create(
            item_id=item.id,
            total_stock=initial_stock,
            optimal_stock_quantity=optimal_stock_quantity,
        )
    
    @classmethod
    def update_stock(cls, instance: Stock, validated_data: dict) -> Stock:
        """Updates a stock record"""
        item = validated_data.get('item') 
        optimal_stock_quantity = validated_data.get('optimal_stock_quantity') 
        total_stock = validated_data.get('total_stock', 0) 

        # Only Allow Total Stock Update if theres not transactions
        if len(instance.get_transactions()) == 0:
            instance.total_stock = total_stock             

        instance.optimal_stock_quantity = optimal_stock_quantity        
        instance.item = item
    
        instance.save()

        return instance

    @classmethod
    def get_current_stock(cls, ingredient_id: int) -> int:
        """Gets the current stock of an ingredient"""
        try:
            stock = Stock.objects.get(ingredient_id=ingredient_id)
            return stock.total_stock
        except Stock.DoesNotExist:
            return 0

    @classmethod
    def get_stock_history(cls, stock_id: int, days: int = 30):
        """Gets the transaction history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return StockTransaction.objects.filter(
            stock_id=stock_id,
            date__gte=cutoff_date
        ).order_by('-date')


    @classmethod
    def delete_stock(cls, stock: Stock) -> int:
        try:
            with transaction.atomic():
                stock.delete()
        except Exception as e:
            logger.error(f"Error deleting table ID {stock.id}: {e}", exc_info=True)
            raise

    @classmethod
    def _validate_not_duplicated_stock(self, item: StockItem=None, ):
        if not item:
            return
        
        is_stock_exisitng = Stock.objects.filter(item=item).exists()
        if is_stock_exisitng:
            raise ValueError('Item Already Have a Stock Track')
        