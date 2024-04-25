from django.urls import path

from .views import user_signup, user_login, user_logout, home, default_view

urlpatterns = [
    path("", default_view, name="default"),
    path("home/", home, name="home"),
    path("accounts/login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("signup/", user_signup, name="signup"),
]
