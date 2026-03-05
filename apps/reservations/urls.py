from django.urls import path, include
from .views.views import (
    update_status_reservation,
    request_user_reservation,
    get_today_reservations,
)

from .views.admin_views import ReservationAdminViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ReservationAdminViewSet, basename='reservation')

urlpatterns = [
    path('admin/', include(router.urls)),

    path('today/', get_today_reservations, name='get-today-reservation'),
    path('<int:reservation_id>/status/<str:new_status>/', update_status_reservation, name='update-reservation-status'),
    path('', request_user_reservation, name='request-user-reservation'),
]