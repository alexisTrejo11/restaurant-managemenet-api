from django.urls import path, include
from .views import (
    DishViewSet,
    list_dish_categories,
    ListActiveDishesByStatus,
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"", DishViewSet, basename="menu")

urlpatterns = [
    path("", include(router.urls)),
    path("dish/categories/", list_dish_categories, name="dish-status-list"),
    path(
        "dish/active/",
        ListActiveDishesByStatus.as_view(),
        name="active-dishes-by-status",
    ),
]
