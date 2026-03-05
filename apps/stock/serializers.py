from rest_framework import serializers
from django.core.validators import MinValueValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import StockItem, Stock, StockTransaction

class StockItemSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True,
        help_text=_('Human-readable category name')
    )
    
    class Meta:
        model = StockItem
        fields = [
            'id',
            'name',
            'unit',
            'category',
            'category_display',
            'menu_item',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_display']
        extra_kwargs = {
            'name': {
                'min_length': 2,
                'max_length': 255,
                'error_messages': {
                    'min_length': _('Name must be at least 2 characters long'),
                    'max_length': _('Name cannot exceed 255 characters')
                }
            },
            'unit': {
                'min_length': 1,
                'max_length': 10,
                'error_messages': {
                    'min_length': _('Unit must be at least 1 character'),
                    'max_length': _('Unit cannot exceed 10 characters')
                }
            },
            'category': {
                'help_text': _('Item classification')
            },
            'menu_item': {
                'help_text': _('Related menu item (for ingredients only)'),
                'required': False
            }
        }

    def validate_name(self, value):
        """Case-insensitive name validation"""
        if StockItem.objects.filter(name__iexact=value).exists():
            if self.instance and self.instance.name.lower() == value.lower():
                return value
            raise serializers.ValidationError(
                _('A stock item with this name already exists')
            )
        return value.strip()

    def validate(self, data):
        """Cross-field validation"""
        if data.get('menu_item') and data.get('category') != 'INGREDIENT':
            raise serializers.ValidationError({
                'menu_item': _('Only ingredients can be linked to menu items')
            })
        return data

class StockTransactionSerializer(serializers.ModelSerializer):
    stock_item_name = serializers.CharField(
        source='stock.item.name',
        read_only=True,
        help_text=_('Name of the related stock item')
    )
    
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True,
        help_text=_('Readable transaction type')
    )

    class Meta:
        model = StockTransaction
        fields = [
            'id',
            'stock',
            'stock_item_name',
            'quantity',
            'transaction_type',
            'transaction_type_display',
            'date',
            'expires_at',
            'employee',
            'notes',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'stock_item_name',
            'transaction_type_display',
            'created_at'
        ]
        extra_kwargs = {
            'quantity': {
                'validators': [MinValueValidator(1, _('Quantity must be at least 1'))],
                'error_messages': {
                    'invalid': _('Enter a valid number'),
                    'min_value': _('Quantity cannot be less than 1')
                }
            },
            'date': {
                'help_text': _('When the transaction occurred')
            },
            'expires_at': {
                'required': False,
                'allow_null': True,
                'help_text': _('Optional expiration date for incoming stock')
            },
            'notes': {
                'required': False,
                'allow_blank': True,
                'max_length': 500,
                'help_text': _('Additional transaction details')
            }
        }

    def validate_quantity(self, value):
        """Context-aware quantity validation"""
        if self.context['request'].method in ['POST', 'PUT', 'PATCH']:
            stock = self.initial_data.get('stock')
            transaction_type = self.initial_data.get('transaction_type')
            
            if transaction_type == 'OUT' and stock:
                current_stock = Stock.objects.get(pk=stock).total_stock
                if value > current_stock:
                    raise serializers.ValidationError(
                        _('Cannot withdraw more than available stock')
                    )
        return value

    def validate_expires_at(self, value):
        """Future date validation"""
        if value and value < timezone.now():
            raise serializers.ValidationError(
                _('Expiration date must be in the future')
            )
        return value

    def create(self, validated_data):
        """Auto-update stock levels on transaction creation"""
        transaction = super().create(validated_data)
        
        stock = transaction.stock
        if transaction.transaction_type == 'IN':
            stock.total_stock += transaction.quantity
        else:
            stock.total_stock -= transaction.quantity
        stock.save()
        
        return transaction


class StockSerializer(serializers.ModelSerializer):
    transactions = serializers.SerializerMethodField(
        help_text="A list of transactions associated with this stock. This field is included only if 'include_transactions=true' is present in the query parameters."
    )
    item_id = serializers.PrimaryKeyRelatedField(
        source='item',
        queryset=StockItem.objects.all(),
        error_messages={
            'does_not_exist': 'The specified inventory item does not exist.',
            'incorrect_type': 'The item ID must be an integer.'
        },
        help_text="The ID of the inventory item associated with this stock record."
    )

    class Meta:
        model = Stock
        fields = ['id', 'item_id', 'total_stock', 'optimal_stock_quantity', 
                'created_at', 'updated_at', 'transactions']
        read_only_fields = ['id', 'created_at', 'updated_at', 'transactions']
        extra_kwargs = {
            'total_stock': {
                'error_messages': {
                    'invalid': 'Stock must be an integer.',
                    'max_value': 'Stock cannot exceed 1,000,000.',
                    'min_value': 'Stock cannot be negative.'
                },
                'validators': [MinValueValidator(0), MaxValueValidator(1_000_000)],
                'help_text': 'The current total quantity of the stock item in inventory.'
            },
            'optimal_stock_quantity': {
                'error_messages': {
                    'invalid': 'Optimal quantity must be an integer.',
                    'max_value': 'Optimal quantity cannot exceed 1,000,000.',
                    'min_value': 'Optimal quantity must be at least 1.'
                },
                'validators': [MinValueValidator(1), MaxValueValidator(1_000_000)],
                'help_text': 'The ideal or optimal quantity of this stock item that should be maintained.'
            }
        }

    def get_transactions(self, obj):
        """Includes transactions only if explicitly requested"""
        request = self.context.get('request')
        if request and request.query_params.get('include_transactions', '').lower() == 'true':
            return StockTransactionSerializer(
                obj.get_transactions(),
                many=True,
                context=self.context
            ).data
        return None

    def validate(self, data):
        """Cross-field validation"""
        total_stock = data.get('total_stock', 0)
        optimal_stock_quantity = data.get('optimal_stock_quantity', 1)

        if total_stock > optimal_stock_quantity * 2:
            raise serializers.ValidationError({
                'total_stock': 'Cannot be more than double the optimal quantity.'
            })
        return data

    def create(self, validated_data):
        """Override to protect auto-generated fields"""
        validated_data.pop('created_at', None)
        validated_data.pop('updated_at', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Override to protect auto-generated fields"""
        validated_data.pop('created_at', None)
        validated_data.pop('updated_at', None)
        return super().update(instance, validated_data)