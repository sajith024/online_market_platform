from django.urls import path

from .views import customer_support

urlpatterns = [
    path("support/chat", customer_support, name="customer_support"),
]
