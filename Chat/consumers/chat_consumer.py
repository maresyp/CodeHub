from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.contrib.auth.models import User
from Chat.models import Message
import json
from django.utils import timezone
from .utils import is_valid_match


class ChatConsumer(AsyncWebsocketConsumer):
    """
    This class defines a WebSocket consumer that handles chat functions.

    :param AsyncWebsocketConsumer: Inherits from Django Channels' AsyncWebsocketConsumer class.
    :type AsyncWebsocketConsumer: class
    """
    PAGE_SIZE = 10

    def __init__(self, *args, **kwargs):
        """
        Initialize the WebSocket consumer instance.

        :param args: Variable length argument list.
        :type args: list
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: dict
        """
        super().__init__(args, kwargs)
        self.room_group_name = None

    async def connect(self):
        """
        Asynchronous method to handle the connection event.
        """
        self.room_group_name = f"chat_{self.scope['user'].id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """
        Asynchronous method to handle receiving data from WebSocket.

        :param text_data: Text data received from the WebSocket.
        :type text_data: str
        :param bytes_data: Binary data received from the WebSocket.
        :type bytes_data: bytes
        """
        if text_data is None:
            return
        text_data_json = json.loads(text_data)

        # Before we do anything, check if the user is in a match with the recipient
        if not is_valid_match(self.scope['user'], text_data_json['recipient']):
            self.chat_error_handler('You are not in a match with this user')
            return

        try:
            match text_data_json['type']:
                case 'chat-message':
                    await self.chat_message_handler(text_data_json)
                case 'recipient-change':
                    await self.recipient_change_handler(text_data_json)
                case 'chat_message_read':
                    await self.chat_message_read_handler(text_data_json)
                case 'chat-request-more-messages':
                    await self.chat_send_more_messages_handler(text_data_json)
        except KeyError:
            return

    async def disconnect(self, close_code):
        """
        Asynchronous method to handle the disconnection event.

        :param close_code: The code for the disconnection event.
        :type close_code: int
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def chat_error_handler(self, error):
        """
        Asynchronous method to handle chat errors.

        :param error: The error message.
        :type error: str
        """
        await self.send(
            text_data=json.dumps({
                'type': 'chat-error',
                'error': error
            })
        )

    async def chat_send_more_messages_handler(self, data):
        """
        Asynchronous method to handle sending more messages.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        @database_sync_to_async
        def get_more_messages():
            last_message = Message.objects.filter(message_id=data['top_message_uuid']).first()
            if not last_message:
                return {}

            messages = Message.objects.filter(
                Q(sender_id=last_message.sender_id, recipient_id=last_message.recipient_id) |
                Q(sender_id=last_message.recipient_id, recipient_id=last_message.sender_id),
                send_timestamp__lt=last_message.send_timestamp
            ).exclude(message_id=data['top_message_uuid']).order_by('-send_timestamp')[:self.PAGE_SIZE]

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
            'type': 'chat-more-messages',
            'messages': await get_more_messages(),
        }))

    async def chat_message_handler(self, data):
        """
        Asynchronous method to handle chat message.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        message = data['message']
        # check if message is not empty
        if not message:
            return

        recipient = await self.get_user(data['recipient'])
        user = await self.get_user(self.scope['user'].id)

        message_id = await self.save_message(user, recipient.id, message)

        # Update the recipient with the new message
        await self.channel_layer.group_send(
            f"chat_{recipient.id}",
            {
                'type': 'chat_message',
                'message': message,
                'message_id': message_id,
                'sender': user,
                'recipient': recipient
            }
        )

    async def chat_message(self, event):
        """
        Asynchronous method to handle sending a chat message.

        :param event: The event data.
        :type event: dict
        """
        await self.send(text_data=json.dumps({
            'type': 'chat-single-message',
            'message': event['message'],
            'message_id': str(event['message_id']),
            'sender': event['sender'].id,
            'recipient': event['recipient'].id,
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }))

    async def recipient_change_handler(self, data):
        """
        Asynchronous method to handle changing recipient.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        await self.send_messages(data['recipient'])

    @database_sync_to_async
    def chat_message_read_handler(self, data):
        """
        Sync to async method to handle reading chat message.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        messages = Message.objects.filter(
            (Q(sender_id=data['recipient'], recipient_id=self.scope['user']) |
             Q(sender_id=self.scope['user'], recipient_id=data['recipient']))
            & Q(view_timestamp__isnull=True)
        )
        for message in messages:
            message.view_timestamp = timezone.now()
            message.is_read = True
            message.save()

    async def send_messages(self, recipient_id):
        """
        Asynchronous method to send messages.

        :param recipient_id: The ID of the recipient.
        :type recipient_id: str
        """
        @database_sync_to_async
        def get_messages():
            start_index = 0
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
        """
        Sync to async method to get a User model instance.

        :param id: The ID of the user.
        :type id: str
        :return: A User model instance.
        :rtype: User
        """
        return User.objects.get(id=id)

    @database_sync_to_async
    def save_message(self, sender, recipient, message):
        """
        Sync to async method to save a chat message.

        :param sender: The sender's ID.
        :type sender: str
        :param recipient: The recipient's ID.
        :type recipient: str
        :param message: The message content.
        :type message: str
        :return: The ID of the saved message.
        :rtype: str
        """
        message_obj = Message.objects.create(
            sender_id=sender,
            recipient_id=User.objects.get(id=recipient),
            body=message
        )
        return message_obj.message_id
