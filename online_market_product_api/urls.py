from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProductsViewSet, CartItemsViewSet, OrderManagementViewSet


router = DefaultRouter()
router.register("products", ProductsViewSet, basename="api_products")
router.register("cartItems", CartItemsViewSet, basename="api_cart_items")
router.register(
    "orderManagement", OrderManagementViewSet, basename="api_order_management"
)

urlpatterns = [path("", include(router.urls))]
