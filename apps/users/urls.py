from django.urls import path, include
from .views import UserModelViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'', UserModelViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),

    #path('search/', views.UserSearchView.as_view(), name='user-search'),
]