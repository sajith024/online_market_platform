from django.db import models

from online_market_app.models import OnlineMarketUser
from online_market_product.models import Product


# Create your models here.
class OrderManagement(models.Model):
    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("processing", "processing"),
        ("failed", "Payment Failed"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(OnlineMarketUser, on_delete=models.CASCADE)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, blank=True
    )
    shipping_address = models.TextField()
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default="pending", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.get_short_name() + " " + str(self.shipping_address)


class Cart(models.Model):
    name = models.CharField(default="Cart One", max_length=50)
    user = models.ForeignKey(OnlineMarketUser, on_delete=models.CASCADE)
    order = models.ForeignKey(
        OrderManagement, on_delete=models.CASCADE, blank=True, null=True, related_name="cart"
    )

    def __str__(self):
        return self.name


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    user = models.ForeignKey(OnlineMarketUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.product)
