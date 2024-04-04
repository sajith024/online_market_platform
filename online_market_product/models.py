from django.db import models

from online_market_app.models import OnlineMarketUser


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="product_images/")
    user = models.ForeignKey(OnlineMarketUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
