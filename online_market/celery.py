import os

from celery import Celery
from django.utils.timezone import timedelta


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "online_market.settings")

app = Celery("online_market")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "send_cart_notification": {
        "task": "online_market_product_api.tasks.send_cart_notification",
        "schedule": timedelta(minutes=1),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
