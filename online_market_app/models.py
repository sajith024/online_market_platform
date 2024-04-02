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
