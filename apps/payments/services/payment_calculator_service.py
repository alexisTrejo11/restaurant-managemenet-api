from decimal import Decimal
from ..models import Payment, PaymentItem
from decimal import Decimal
from typing import List

class PaymentCalculatorService:
    DEFAULT_VAT_RATE = Decimal('0.16')  # 16%

    @classmethod
    def calculate_payment_totals(cls, payment: Payment, items: List[PaymentItem]):
        if len(items) == 0:
            raise ValueError("Item List is Empty")    
    
        sub_total = sum(item.total for item in items)
        discount = Decimal('0.00')
        vat = sub_total * cls.DEFAULT_VAT_RATE
        
        payment.sub_total = sub_total
        payment.discount = discount
        payment.vat_rate = cls.DEFAULT_VAT_RATE
        payment.vat = vat
        payment.total = (sub_total + vat) - discount
   
    @classmethod
    def calculate_item_base_price(cls, unit_price, quantity) -> Decimal:
        return unit_price * quantity
    
    @classmethod
    def calculate_item_total_price(cls, base_price, extra_price) -> Decimal:
        return base_price + extra_price

    @classmethod
    def calculate_menu_extra_charges(cls, menu_extra) -> Decimal:
        return menu_extra.price if menu_extra else Decimal("0.00")
    
    