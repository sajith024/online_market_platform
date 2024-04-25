from django.urls import path

from .views import customer_support, community

urlpatterns = [
    path("support/chat", customer_support, name="customer_support"),
    path("support/chat/community", community, name="community"),
]
