from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tables.views import TableViewSet

router = DefaultRouter()
router.register(r"tables", TableViewSet, basename="table")

urlpatterns = [
    # Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/", include(router.urls)),
    path("api/v1/auth/", include("apps.authorization.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/menu/", include("apps.menu.urls")),
    path("api/v1/stock/", include("apps.stock.urls")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/reservations/", include("apps.reservations.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
]
