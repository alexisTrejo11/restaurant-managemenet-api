from django.urls import path
from .views import login, signup, logout_all, logout_view

urlpatterns = [
    path("signup/", signup, name="signup"),
    path("login/", login, name="login"),
    path("logout/", logout_view, name="logout"),
    path("logout-all/", logout_all, name="logout_all"),
]
