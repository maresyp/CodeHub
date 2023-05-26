from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
import json
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    PAGE_SIZE = 10

    async def connect(self):
        self.room_group_name = 'test'
        self.page_number = 1

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        user = await self.get_user()
        print(f"User {user.username} connected")

        # Fetch messages from the database
        messages = await self.get_messages()
        await self.accept()

        # Send messages to the client
        await self.send_messages(messages)


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        user = await self.get_user()
        await self.save_message(user, message)

        # Update the client with the new message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'username':user.username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'type':'chat',
            'message': message,
            'username': username
        }))

    async def scroll_messages(self, event):
        direction = event['direction']

        if direction == 'up':
            self.page_number += 1
        elif direction == 'down':
            self.page_number -= 1

        messages = await self.get_messages()
        await self.send_messages(messages)

    async def send_messages(self, messages):
        for message in messages:
            data = await self.get_message_data(message)
            timestamp_str = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            await self.send(text_data=json.dumps({
                'type': 'chat',
                'message': data['message'],
                'username': data['username'],
                'timestamp': timestamp_str
            }))

    @database_sync_to_async
    def get_user(self):
        return User.objects.get(id=self.scope['user'].id)

    @database_sync_to_async
    def save_message(self, user, message):
        Message.objects.create(
            sender_id = user,
            body = message
        )

    @database_sync_to_async
    def get_messages(self):
        start_index = (self.page_number - 1) * self.PAGE_SIZE
        end_index = start_index + self.PAGE_SIZE
        return list(Message.objects.order_by('send_timestamp')[start_index:end_index])

    @database_sync_to_async
    def get_message_data(self, message):
        return {
            'message': message.body,
            'username': message.sender_id.username,
            'timestamp': message.send_timestamp
        }
