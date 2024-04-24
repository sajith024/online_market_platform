import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if self.user is None:
            raise DenyConnection()

        self.chat_group = await self.user_group_name(self.user.username)
        await self.channel_layer.group_add(self.chat_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.user is not None:
            await self.channel_layer.group_discard(self.chat_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        receiver = data["receiver"]

        await self.channel_layer.group_send(
            await self.user_group_name(receiver),
            {
                "type": "chat.message",
                "message": message,
                "sender": self.user.username,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        await self.send(text_data=json.dumps({"message": message, "sender": sender}))

    async def user_group_name(self, username):
        return f"user_{username}"


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        if self.user is None:
            raise DenyConnection()

        self.request_group = self.scope["url_route"]["kwargs"]["group_name"]
        self.group_name = f"chat_{self.request_group}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()
        await self.send(
            text_data=json.dumps(
                {"message": f"User: {self.user.username} joined the conversation."}
            )
        )

    async def disconnect(self, close_code):
        if self.user is not None:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.group_name, {"type": "chat.message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
