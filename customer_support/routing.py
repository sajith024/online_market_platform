from django.urls import re_path

from .consumers import GroupChatConsumer, ChatConsumer

websocket_urlpatterns = [
    re_path(r"^ws/chat/(?P<chat_name>[\w-]+)/$", ChatConsumer.as_asgi()),
    re_path(r"^ws/chat/group/(?P<group_name>[\w-]+)/$", GroupChatConsumer.as_asgi()),
]
