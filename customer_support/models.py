from django.db import models

from online_market_app.models import OnlineMarketUser


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=30, unique=True)
    members = models.ManyToManyField(OnlineMarketUser)
        
    def __str__(self) -> str:
        return f"Group {self.name}"

class Message(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    author = models.ForeignKey(OnlineMarketUser, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")

    def __str__(self) -> str:
        return f"{self.author}:- {self.content}"

class Chat(models.Model):
    name = models.CharField(max_length=30, unique=True)
    members = models.ManyToManyField(OnlineMarketUser)
        
    def __str__(self) -> str:
        return f"Chat {self.name}"

class ChatMessage(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    author = models.ForeignKey(OnlineMarketUser, on_delete=models.CASCADE, related_name="sended_message")
    receiver = models.ForeignKey(OnlineMarketUser, on_delete=models.CASCADE, related_name="recived_message")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")

    def __str__(self) -> str:
        return f"{self.author}:- {self.content}"