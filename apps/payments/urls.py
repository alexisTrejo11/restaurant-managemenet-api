from django.urls import path, include
from .views import PaymentAdminViews
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', PaymentAdminViews, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
]