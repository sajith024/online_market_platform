from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductsViewSet


router = DefaultRouter()
router.register("products", ProductsViewSet, basename="api_products")

urlpatterns = [path("", include(router.urls))]
