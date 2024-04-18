from celery import shared_task

from django.conf import settings

from online_market_product_api.models import Cart


@shared_task
def send_cart_notification():
    carts = Cart.objects.filter(order__isnull=True).distinct("user")
    for items in carts:
        user = items.user
        subject = "Reminder: Complete Your Purchase!"
        message = "Dear {},\n\nYou have items in your cart. Please complete your purchase and avail a discount for 50%  \soon.".format(
            user.username
        )

        user.email_user(subject, message, settings.EMAIL_HOST_USER)
