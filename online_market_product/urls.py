from django.urls import path

from .views import (
    add_product,
    edit_product,
    delete_product,
    search_product,
    filter_product,
    product_payment,
    payment_success,
)

urlpatterns = [
    path("add/", add_product, name="add_product"),
    path("edit/<int:pk>/", edit_product, name="edit_product"),
    path("delete/<int:pk>/", delete_product, name="delete_product"),
    path("search/", search_product, name="search_product"),
    path("filter/", filter_product, name="filter_product"),
    path("payments/product_payment/<int:pk>/", product_payment, name="product_payment"),
    path("payments/success/", payment_success, name="checkout_success"),
]
