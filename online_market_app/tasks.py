from celery import shared_task

from django.conf import settings

from .models import OnlineMarketUser


@shared_task
def send_signup_confirmation_email(user_id):
    user = OnlineMarketUser.objects.get(pk=user_id)

    subject = "Welcome to Our Online Market Platform!"

    role = user.role.name
    if role == "Buyer":
        message = f"Dear {user.username},\n\nPlease Confirm Your email!.\n\nThank you for signing up! Buyer"
    elif role == "Seller":
        message = f"Dear {user.username},\n\nPlease Confirm Your email!.\n\nThank you for signing up! Seller"
    else:
        message = f"Dear {user.username},\n\nPlease Confirm Your email!.\n\nThank you for signing up!"

    user.email_user(subject, message, settings.EMAIL_HOST_USER)
