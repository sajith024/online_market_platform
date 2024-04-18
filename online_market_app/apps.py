from django.apps import AppConfig


class OnlineMarketAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "online_market_app"

    def ready(self):
        import online_market_app.signals
