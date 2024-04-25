from django.contrib import admin

from .models import Message, Group, Chat, ChatMessage

# Register your models here.
admin.site.register(Message)
admin.site.register(Group)
admin.site.register(Chat)
admin.site.register(ChatMessage)