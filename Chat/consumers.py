from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
import json


class ChatConsumer(AsyncWebsocketConsumer):
    PAGE_SIZE = 10

    async def connect(self):
        self.room_group_name = f"chat_{self.scope['user'].id}"
        self.page_number = 1

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        user = await self.get_user(self.scope['user'].id)
        print(f"User {user.username} connected")

        # Fetch messages from the database
        messages = await self.get_messages()
        await self.accept()

        # Send messages to the client
        await self.send_messages(messages)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        recipient = await self.get_user(text_data_json['recipient'])
        user = await self.get_user(self.scope['user'].id)

        # TODO: check if user and recipiend are matched before saving the message
        await self.save_message(user, recipient.id, message)

        # Update the client with the new message
        await self.channel_layer.group_send(
            f"chat_{recipient.id}",
            {
                'type': 'chat_message',
                'message': message,
                'sender': user,
                'recipient': recipient
            }
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user,
                'recipient': recipient
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        recipient = event['recipient']

        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message,
            'sender': sender.username,
            'recipient': recipient.username,
            'timestamp': 'now'
        }))

    async def send_messages(self, messages):
        for message in messages:
            data = await self.get_message_data(message)
            timestamp_str = data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            await self.send(text_data=json.dumps({
                'type': 'chat',
                'message': data['message'],
                'sender': data['sender'],
                'recipient': data['recipient'],
                'timestamp': timestamp_str
            }))

    @database_sync_to_async
    def get_user(self, id: str):
        return User.objects.get(id=id)

    @database_sync_to_async
    def save_message(self, sender, recipient, message):
        print(recipient)
        Message.objects.create(
            sender_id=sender,
            recipient_id=User.objects.get(id=recipient),
            body=message
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
            'sender': message.sender_id.username,
            'recipient': message.recipient_id.username,
            'timestamp': message.send_timestamp
        }
