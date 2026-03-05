from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class StockItem(models.Model):
    class CategoryChoices(models.TextChoices):
        INGREDIENT = 'INGREDIENT', _('Ingredient')
        UTENSIL = 'UTENSIL', _('Utensil')
        CONTAINER = 'CONTAINER', _('Container')
        OTHER = 'OTHER', _('Other')

    menu_item = models.ForeignKey(
        'menu.Dish',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_items',
        verbose_name=_('Menu Item'),
        help_text=_('Associated menu item (for ingredients only)')
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
        help_text=_('Descriptive name of the item'),
        unique=True
    )
    
    unit = models.CharField(
        max_length=10,
        verbose_name=_('Unit of Measurement'),
        help_text=_('Measurement unit (e.g., kg, lb, units)')
    )
    
    category = models.CharField(
        max_length=15,
        choices=CategoryChoices.choices,
        default=CategoryChoices.OTHER,
        verbose_name=_('Category'),
        help_text=_('Classification of the stock item')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_('Updated At')
    )

    class Meta:
        db_table = 'stock_items'
        verbose_name = _('Stock Item')
        verbose_name_plural = _('Stock Items')
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                name='unique_stock_item_name'
            ),
            models.CheckConstraint(
                check=models.Q(unit__isnull=False) & ~models.Q(unit=''),
                name='non_empty_unit'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def clean(self):
        super().clean()
        if not self.name or len(self.name.strip()) == 0:
            raise ValidationError({'name': _('Name cannot be empty')})
        
        if not self.unit or len(self.unit.strip()) == 0:
            raise ValidationError({'unit': _('Unit cannot be empty')})
        
        if self.menu_item and self.category != self.CategoryChoices.INGREDIENT:
            raise ValidationError({
                'menu_item': _('Only ingredients can be linked to menu items')
            })

class Stock(models.Model):
    item = models.ForeignKey(
        StockItem,
        on_delete=models.PROTECT,
        related_name='stocks',
        verbose_name=_('Stock Item')
    )
    
    total_stock = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0, _('Stock cannot be negative')),
            MaxValueValidator(1000000, _('Stock cannot exceed 1,000,000'))
        ],
        verbose_name=_('Current Stock')
    )
    
    optimal_stock_quantity = models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1, _('Optimal stock must be at least 1')),
            MaxValueValidator(1000000, _('Optimal stock cannot exceed 1,000,000'))
        ],
        verbose_name=_('Optimal Quantity')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name=_('Updated At')
    )

    class Meta:
        db_table = 'stocks'
        verbose_name = _('Inventory')
        verbose_name_plural = _('Inventories')
        ordering = ['-updated_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(total_stock__gte=0),
                name='non_negative_stock'
            ),
            models.CheckConstraint(
                check=models.Q(optimal_stock_quantity__gte=1),
                name='minimum_optimal_stock'
            ),
            models.UniqueConstraint(
                fields=['item'],
                name='unique_item_inventory'
            )
        ]

    def __str__(self):
        return f"{self.item.name} - {self.total_stock} {self.item.unit}"
        
    def get_transactions(self):
        return self.transactions.all().order_by('-date')

    def clean(self):
        super().clean()
        if self.total_stock > self.optimal_stock_quantity * 3:
            raise ValidationError({
                'total_stock': _('Current stock cannot be more than 3x the optimal quantity')
            })

class StockTransaction(models.Model):
    class TransactionType(models.TextChoices):
        IN = 'IN', _('Stock In')
        OUT = 'OUT', _('Stock Out')

    stock = models.ForeignKey(
        Stock,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name=_('Inventory')
    )
    
    quantity = models.IntegerField(
        validators=[
            MinValueValidator(1, _('Quantity must be at least 1')),
            MaxValueValidator(10000, _('Quantity cannot exceed 10,000'))
        ],
        verbose_name=_('Quantity')
    )
    
    transaction_type = models.CharField(
        max_length=3,
        choices=TransactionType.choices,
        verbose_name=_('Type')
    )
    
    date = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Transaction Date')
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Expiration Date')
    )
    
    employee = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_transactions',
        verbose_name=_('Processed By')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_('Created At')
    )

    class Meta:
        db_table = 'stock_transactions'
        verbose_name = _('Inventory Transaction')
        verbose_name_plural = _('Inventory Transactions')
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['date']),
            models.Index(fields=['stock', 'date'])
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.quantity} {self.stock.item.unit}"

    def clean(self):
        super().clean()
        
        if self.transaction_type == self.TransactionType.OUT:
            if self.quantity > self.stock.total_stock:
                raise ValidationError({
                    'quantity': _('Cannot withdraw more than current stock')
                })
        
        if self.expires_at and self.expires_at < timezone.now():
            raise ValidationError({
                'expires_at': _('Expiration date cannot be in the past')
            })