from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
import json


class VideoConsumer(AsyncWebsocketConsumer):
    PAGE_SIZE = 10

    async def connect(self):
        await self.accept()