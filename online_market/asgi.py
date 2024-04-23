"""
ASGI config for online_market project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from customer_support.middlewares import WebSocketJWTAuthMiddleware
from customer_support.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "online_market.settings")

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": WebSocketJWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
