import json

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from asgiref.sync import async_to_sync
from django.db.models import Q

from online_market_app.models import OnlineMarketUser
from .models import Message, Group, Chat, ChatMessage


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope.get("user")
        if self.user is None:
            raise DenyConnection()

        self.request_chat = self.scope["url_route"]["kwargs"]["chat_name"]
        username = self.user.get_username()
        self.chat = Chat.objects.get_or_create(name=self.user_group_name(username))[0]
        self.reciever = OnlineMarketUser.objects.get(username=self.request_chat)

        if self.user not in self.chat.members.all():
            self.chat.members.add(self.user)
            self.chat.save()

        async_to_sync(self.channel_layer.group_add)(self.chat.name, self.channel_name)
        self.accept()

        messages = ChatMessage.objects.filter(
            Q(receiver=self.reciever, author=self.user)
            | Q(author=self.reciever, receiver=self.user)
        )
        for message in messages:
            self.send(
                text_data=json.dumps(
                    {
                        "type": "chat.message",
                        "message": message.content,
                        "sender": f"{message.author}",
                    }
                )
            )

    def disconnect(self, close_code):
        if self.user is not None:
            async_to_sync(self.channel_layer.group_discard)(
                self.chat.name, self.channel_name
            )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        message = ChatMessage.objects.create(
            content=message,
            author=self.user,
            chat=self.chat,
            receiver=self.reciever,
        )
        async_to_sync(self.channel_layer.group_send)(
            self.user_group_name(self.request_chat),
            {
                "type": "chat.message",
                "message": message.content,
                "sender": f"{message.author}",
            },
        )

    def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        self.send(text_data=json.dumps({"message": message, "sender": sender}))

    def user_group_name(self, username):
        return f"user_{username}"


class GroupChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope.get("user")
        if self.user is None:
            raise DenyConnection()

        request_group = self.scope["url_route"]["kwargs"]["group_name"]

        self.group = Group.objects.get_or_create(name=f"chat_{request_group}")[0]

        if self.user not in self.group.members.all():
            self.group.members.add(self.user)
            self.group.save()

        async_to_sync(self.channel_layer.group_add)(self.group.name, self.channel_name)
        self.accept()

        async_to_sync(self.channel_layer.group_send)(
            self.group.name,
            {
                "type": "chat.message",
                "message": f"{self.user.username} joined the conversation.",
                "sender": "Group",
            },
        )

        messages = Message.objects.filter(group=self.group)
        for message in messages:
            self.send(
                text_data=json.dumps(
                    {
                        "type": "chat.message",
                        "message": message.content,
                        "sender": f"{message.author}",
                    }
                )
            )

    def disconnect(self, close_code):
        if self.user is not None:
            async_to_sync(self.channel_layer.group_send)(
                self.group.name,
                {
                    "type": "chat.message",
                    "message": f"{self.user.username} left the conversation.",
                    "sender": "Group",
                },
            )
            async_to_sync(self.channel_layer.group_discard)(
                self.group.name, self.channel_name
            )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        message = Message.objects.create(
            content=message, author=self.user, group=self.group
        )
        async_to_sync(self.channel_layer.group_send)(
            self.group.name,
            {
                "type": "chat.message",
                "message": message.content,
                "sender": f"{message.author}",
            },
        )

    def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]

        self.send(text_data=json.dumps({"message": message, "sender": sender}))
