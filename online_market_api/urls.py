from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegistrationUserView,
    LoginUserView,
    LogoutUserView,
    SMSVerificationView,
    OTPVerificationView,
    RolesViewSet,
)


router = DefaultRouter()
router.register("roles", RolesViewSet, basename="api_role")

urlpatterns = [
    path("signup/", RegistrationUserView.as_view(), name="api_signup"),
    path("login/", LoginUserView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="api_logout"),
    path("send_sms/", SMSVerificationView.as_view(), name="api_send_sms"),
    path("verify_phone/", OTPVerificationView.as_view(), name="api_verify_phone"),
    path("", include(router.urls)),
]
