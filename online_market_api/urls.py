from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegistrationUserView, RolesViewSet, send_sms_code, verify_phone


router = DefaultRouter()
router.register("roles", RolesViewSet, basename="api_role")

urlpatterns = [
    path("signup/", RegistrationUserView.as_view(), name="api_signup"),
    path("", include(router.urls)),
    path("send_sms/", send_sms_code, name="api_send_sms"),
    path("verify_phone/", verify_phone, name="api_verify_phone"),
]
