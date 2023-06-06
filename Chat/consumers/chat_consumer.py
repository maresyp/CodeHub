from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.contrib.auth.models import User
from Chat.models import Message
import json
from django.utils import timezone
from .utils import is_valid_match

class ChatConsumer(AsyncWebsocketConsumer):
    PAGE_SIZE = 10

    async def connect(self):
        self.room_group_name = f"chat_{self.scope['user'].id}"
        self.page_number = 1

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        text_data_json = json.loads(text_data)

        # Before we do anything, check if the user is in a match with the recipient
        if not is_valid_match(self.scope['user'], text_data_json['recipient']):
            # TODO: maybe add some error message
            return

        try:
            match text_data_json['type']:
                case 'chat-message':
                    await self.chat_message_handler(text_data_json)
                case 'recipient-change':
                    await self.recipient_change_handler(text_data_json)
                case 'chat_message_read':
                    await self.chat_message_read_handler(text_data_json)
        except KeyError:
            return

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def chat_message_handler(self, data):
        message = data['message']
        recipient = await self.get_user(data['recipient'])
        user = await self.get_user(self.scope['user'].id)

        await self.save_message(user, recipient.id, message)

        # Update the recipient with the new message
        await self.channel_layer.group_send(
            f"chat_{recipient.id}",
            {
                'type': 'chat_message',
                'message': message,
                'sender': user,
                'recipient': recipient
            }
        )

    async def recipient_change_handler(self, data):
        await self.send_messages(data['recipient'])

    @database_sync_to_async
    def chat_message_read_handler(self, data):
        messages = Message.objects.filter(
            (Q(sender_id=data['recipient'], recipient_id=self.scope['user']) |
             Q(sender_id=self.scope['user'], recipient_id=data['recipient']))
            & Q(view_timestamp__isnull=True)
        )

        if messages:
            messages.update(view_timestamp=timezone.now())

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat-single-message',
            'message': event['message'],
            'sender': event['sender'].id,
            'recipient': event['recipient'].id,
            'timestamp': 'now'
        }))

    async def send_messages(self, recipient_id):
        @database_sync_to_async
        def get_messages():
            start_index = (self.page_number - 1) * self.PAGE_SIZE
            end_index = start_index + self.PAGE_SIZE

            messages = Message.objects.filter(
                Q(sender_id=self.scope['user'], recipient_id=recipient_id) |
                Q(sender_id=recipient_id, recipient_id=self.scope['user'])
            ).order_by('-send_timestamp')[start_index:end_index]

            messages_data = {
                str(msg.message_id): {
                    'message': msg.body,
                    'sender': msg.sender_id.id,
                    'recipient': msg.recipient_id.id,
                    'timestamp': msg.send_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                } for msg in messages
            }

            return messages_data

        await self.send(text_data=json.dumps({
            'type': 'chat-new-window',
            'messages': await get_messages(),
        }))

    @database_sync_to_async
    def get_user(self, id: str):
        return User.objects.get(id=id)

    @database_sync_to_async
    def save_message(self, sender, recipient, message):
        Message.objects.create(
            sender_id=sender,
            recipient_id=User.objects.get(id=recipient),
            body=message
        )
