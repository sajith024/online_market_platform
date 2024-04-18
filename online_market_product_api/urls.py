from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ProductsViewSet,
    CartViewSet,
    CartItemsViewSet,
    OrderManagementViewSet,
    OnlineMarketPaymentViewSet,
)


router = DefaultRouter()
router.register("products", ProductsViewSet, basename="api_products")
router.register("cart", CartViewSet, basename="api_cart")
router.register("cartItems", CartItemsViewSet, basename="api_cart_items")
router.register(
    "orderManagement", OrderManagementViewSet, basename="api_order_management"
)
router.register("payments", OnlineMarketPaymentViewSet, basename="api_payments")

urlpatterns = [path("", include(router.urls))]
