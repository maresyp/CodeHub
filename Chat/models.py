from django.db import models
import uuid
from Users.models import User

# Create your models here.

class Message(models.Model):
    message_id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_id')
    recipient_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_id')
    body = models.TextField(max_length=5000)
    # attachment =  ???
    is_read = models.BooleanField(default=False)
    send_timestamp = models.DateTimeField(auto_now_add=True)
    # view_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.message_id)