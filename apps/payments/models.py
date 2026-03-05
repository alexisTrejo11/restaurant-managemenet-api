from django.db import models
from django.db.models import Q
from decimal import Decimal
from django.utils import timezone
from datetime import datetime

class PaymentQuerySet(models.QuerySet):
    """Custom QuerySet for Payment model with dynamic search capabilities."""
    
    def dynamic_search(self, search_params: dict):
        """
        Perform dynamic search based on multiple parameters.
        
        Args:
            search_params: Dictionary containing search parameters:
                - search: General text search
                - payment_method: Filter by payment method
                - payment_status: Filter by payment status
                - currency_type: Filter by currency
                - date_from: Filter by start date
                - date_to: Filter by end date
                - amount_min: Minimum amount
                - amount_max: Maximum amount
                
        Returns:
            Filtered QuerySet
        """
        queryset = self.filter(deleted_at__isnull=True)
        
        # Text search 
        if search_params.get('search'):
            search_term = search_params['search']
            queryset = queryset.filter(
                Q(order__id__icontains=search_term) |
                Q(payment_method__icontains=search_term) |
                Q(payment_status__icontains=search_term) |
                Q(currency_type__icontains=search_term) |
                Q(payment_items__menu_item__name__icontains=search_term)
            ).distinct()
        
        if search_params.get('payment_method'):
            queryset = queryset.filter(payment_method=search_params['payment_method'])
        
        if search_params.get('payment_status'):
            queryset = queryset.filter(payment_status=search_params['payment_status'])
        
        if search_params.get('currency_type'):
            queryset = queryset.filter(currency_type=search_params['currency_type'])
        
        if search_params.get('date_from'):
            try:
                date_from = datetime.strptime(search_params['date_from'], '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__gte=date_from)
            except ValueError:
                pass
        
        if search_params.get('date_to'):
            try:
                date_to = datetime.strptime(search_params['date_to'], '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__lte=date_to)
            except ValueError:
                pass
        
        if search_params.get('amount_min'):
            try:
                queryset = queryset.filter(total__gte=Decimal(search_params['amount_min']))
            except:
                pass
        
        if search_params.get('amount_max'):
            try:
                queryset = queryset.filter(total__lte=Decimal(search_params['amount_max']))
            except:
                pass
        
        return queryset

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Card'),
        ('TRANSACTION', 'Transaction'),
    ]
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('REFUNDED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    CURRENCY_TYPES = [
        ('MXN', 'Mexican Peso'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    ]

    order = models.OneToOneField('orders.Order', on_delete=models.PROTECT, null=True, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    vat = models.DecimalField(max_digits=10, decimal_places=2,  default=Decimal('0.00'))
    currency_type = models.CharField(max_length=3, choices=CURRENCY_TYPES)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = PaymentQuerySet.as_manager()

    @staticmethod
    def from_order(order):
        return Payment(
            total = Decimal('0.00'),
            sub_total = Decimal('0.00'),
            vat = Decimal('0.00'),
            vat_rate = Decimal('0.00'),
            discount = Decimal('0.00'),
            currency_type = "MXN",
            order = order,
            payment_status = 'PENDING',
        )
    
    @staticmethod
    def get_default():
        return Payment(
            total = Decimal('0.00'),
            sub_total = Decimal('0.00'),
            vat = Decimal('0.00'),
            vat_rate = Decimal('0.00'),
            discount = Decimal('0.00'),
            currency_type = "MXN",
            payment_status = 'PENDING',
        )


    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        db_table = 'payments'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'Payment for Order {self.order_id} - {self.total} {self.currency_type}'

class PaymentItem(models.Model):
    payment = models.ForeignKey(
        'Payment', 
        on_delete=models.CASCADE, 
        related_name='payment_items'
    )
    order_item = models.OneToOneField(
        'orders.OrderItem', 
        on_delete=models.PROTECT, 
        related_name='payment_item',
        null=True, 
        blank=True, 
    )
    menu_item = models.ForeignKey(
        'menu.Dish', 
        on_delete=models.PROTECT, 
        related_name='payment_items',
        null=True, 
        blank=True, 
    )
    menu_item_extra = models.ForeignKey(
        'menu.MenuExtra', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payment_items'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    extras_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Valor por defecto
    total = models.DecimalField(max_digits=10, decimal_places=2)
    charge_description = models.CharField(max_length=255, default='')

    class Meta:
        db_table = 'payment_items'
        verbose_name = 'Payment Item'
        verbose_name_plural = 'Payment Items'

    def __str__(self):
        return f'{self.quantity}x {self.menu_item.name} - {self.total}'
