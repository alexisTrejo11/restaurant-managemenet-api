from django.urls import path
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tables.views import TableViews

schema_view = get_schema_view(
    openapi.Info(
        title="Restaurant Management API",
        default_version="v1",
        description="Documentation for the API of a Restaurant Management System",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="marcoalexispt.02@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)

router = DefaultRouter()
router.register(r"tables", TableViews, basename="table")

urlpatterns = [
    # Swagger
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("v1/api/", include(router.urls)),
    path("v1/api/auth/", include("apps.authorization.urls")),
    path("v1/api/users/", include("apps.users.urls")),
    path("v1/api/menu/", include("apps.menu.urls")),
    path("v1/api/stock/", include("apps.stock.urls")),
    path("v1/api/orders/", include("apps.orders.urls")),
    path("v1/api/reservations/", include("apps.reservations.urls")),
    path("v1/api/payments/", include("apps.payments.urls")),
]
