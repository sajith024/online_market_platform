from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.utils import timezone

from online_market_app.models import OnlineMarketUser


# Create your models here.
class OnlineMarketLogs(models.Model):
    log_date = models.DateTimeField(auto_now_add=True)
    request_method = models.CharField()
    request_path = models.CharField()
    request_status = models.SmallIntegerField()
    response = models.JSONField()

    def __str__(self) -> str:
        return self.log_date


class OnlineMarketOTP(models.Model):
    user = models.OneToOneField(OnlineMarketUser, on_delete=models.CASCADE)
    key = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.otp
