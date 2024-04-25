from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import OnlineMarketUserManager


class Role(models.Model):
    name = models.CharField(unique=True)

    def __str__(self) -> str:
        return self.name


class OnlineMarketUser(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    objects = OnlineMarketUserManager()
    
    def __str__(self) -> str:
            return self.get_username()

class OnlineMarketStripeCustomer(models.Model):
    client_id = models.CharField(unique=True)
    user = models.OneToOneField(
        OnlineMarketUser, on_delete=models.CASCADE, related_name="stripe_customer"
    )

    def __str__(self) -> str:
        return self.user.get_username()
