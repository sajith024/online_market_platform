from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OnlineMarketUser
from .tasks import send_signup_confirmation_email


@receiver(post_save, sender=OnlineMarketUser)
def user_created(sender, instance, created, **kwargs):
    if created:
        send_signup_confirmation_email.delay_on_commit(instance.id)
