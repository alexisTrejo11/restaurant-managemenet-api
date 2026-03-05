from ..models import Payment, PaymentItem
from apps.orders.models import Order, OrderItem
from .payment_item_service import PaymentItemService as ItemService
from .payment_calculator_service import PaymentCalculatorService as CalculatorService


class PaymentService:
    FILTER_MAPPING = {
        "q": "search",
        "method": "payment_method",
        "status": "payment_status",
        "currency": "currency_type",
        "from": "date_from",
        "to": "date_to",
        "min_amount": "amount_min",
        "max_amount": "amount_max",
    }

    @classmethod
    def get_applied_filter_names(cls, search_params) -> list:
        """Return just the names of filters that were applied"""
        return [cls.FILTER_MAPPING.get(k, k) for k in search_params.keys()]

    @classmethod
    def get_search_params(cls, query_params) -> dict:
        search_params = {
            "search": query_params.get("q", None),
            "payment_method": query_params.get("method", None),
            "payment_status": query_params.get("status", None),
            "currency_type": query_params.get("currency", None),
            "date_from": query_params.get("from", None),
            "date_to": query_params.get("to", None),
            "amount_min": query_params.get("min_amount", None),
            "amount_max": query_params.get("max_amount", None),
        }
        search_params = {k: v for k, v in search_params.items() if v is not None}
        return search_params

    @classmethod
    def create_payment_from_order(cls, order: Order) -> Payment:
        payment = Payment.from_order(order)
        payment.save()
        try:
            payment_items = ItemService.generate_items_from_order(
                order.order_items.all(), payment
            )
            ItemService.save_items(payment_items)

            CalculatorService.calculate_payment_totals(payment, payment_items)
            payment.save()

            return payment
        except Exception as e:
            payment.delete()
            raise e

    @classmethod
    def create_payment(cls, payment_data: dict) -> Payment:
        items = payment_data.get("payment_items")
        payment = Payment.get_default()
        payment.save()
        try:
            payment_items = ItemService.generate_items(payment, items)
            ItemService.save_items(payment_items)

            CalculatorService.calculate_totals(payment, payment_items)
            payment.save()

            return payment

        except Exception as e:
            payment.delete()
            raise e

    @classmethod
    def update_payment(cls, payment: Payment, payment_data: dict):
        pass

    @classmethod
    def delete_payment(cls, payment: Payment, hard_delete=False):
        if hard_delete:
            payment.delete()
        else:
            payment.soft_delete()
