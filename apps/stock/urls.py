from django.urls import path, include
from .views.stock_transaction_views import (
    register_transaction,
    update_transaction,
    delete_transaction,
)

from .views.stock_views import StockViews as StockViewSet
from .views.stock_item_views import StockItemViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", StockViewSet, basename="stock")
router.register(r"(?P<stock_pk>\d+)/items", StockItemViewSet, basename="stock-item")

urlpatterns = [
    path("", include(router.urls)),
    path("transactions/", register_transaction, name="register-transaction"),
    path(
        "transactions/<int:transaction_id>/",
        update_transaction,
        name="update-transaction",
    ),
    path(
        "transactions/<int:transaction_id>/delete/",
        delete_transaction,
        name="delete-transaction",
    ),
]
