from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        token = self.get_token(scope)
        if token:
            try:
                validated_token = JWTAuthentication().get_validated_token(token)
                scope["user"] = await self.get_user(validated_token)
            except InvalidToken:
                scope["user"] = None

        return await self.inner(scope, receive, send)

    def get_token(self, scope):
        parsed_query_string = parse_qs(scope["query_string"])
        data = parsed_query_string.get(b"token")
        if data:
            token = data[0].decode("utf-8")
        else:
            token = None
        return token

    @database_sync_to_async
    def get_user(self, validated_token):
        User = get_user_model()
        user_id = validated_token["user_id"]
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
