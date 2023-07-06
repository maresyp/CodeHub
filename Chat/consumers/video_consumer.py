from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .utils import is_valid_match


class VideoConsumer(AsyncWebsocketConsumer):
    """
    This class defines a WebSocket consumer that handles video call functionality.

    :param AsyncWebsocketConsumer: Inherits from Django Channels' AsyncWebsocketConsumer class.
    :type AsyncWebsocketConsumer: class
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the WebSocket consumer instance. Set up room_group_name to None.

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
        Sets up the user's group and adds the connection to the channel layer.
        """
        self.room_group_name = f"video_{self.scope['user'].id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        """
        Asynchronous method to handle receiving data from WebSocket.
        Uses a match-case structure to handle different types of received messages.

        :param text_data: Text data received from the WebSocket.
        :type text_data: str
        :param bytes_data: Binary data received from the WebSocket.
        :type bytes_data: bytes
        """
        if text_data is None:
            return
        text_data_json = json.loads(text_data)

        if not is_valid_match(self.scope['user'], text_data_json['recipient']):
            # TODO: add some error message
            return

        try:
            match text_data_json['type']:
                case 'video_offer':
                    await self.video_offer_handler(text_data_json)
                case 'video_answer':
                    await self.video_answer_handler(text_data_json)
                case 'new-ice-candidate':
                    await self.new_ice_candidate_handler(text_data_json)
                case 'end_call':
                    await self.end_call_handler(text_data_json)
                case 'video_rejected':
                    await self.video_rejected_handler(text_data_json)
        except KeyError:
            return

    async def video_offer_handler(self, data):
        """
        Asynchronous method to handle video offer.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'video_offer',
                'caller_name': self.scope['user'].username,
                'recipient': self.scope['user'].id,
                'offer': data['offer'],
            }
        )

    async def video_offer(self, data):
        """
        Asynchronous method to send video offer.

        :param data: The event data.
        :type data: dict
        """
        await self.send(text_data=json.dumps({
            'type': 'video_offer',
            'caller_name': data['caller_name'],
            'recipient': data['recipient'],
            'offer': data['offer'],
        }))

    async def video_answer_handler(self, data):
        """
        Asynchronous method to handle video answer.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'video_result',
                'recipient': self.scope['user'].id,
                'answer': data['answer'],
            }
        )

    async def video_result(self, data):
        """
        Asynchronous method to send video result.

        :param data: The event data.
        :type data: dict
        """
        await self.send(text_data=json.dumps({
            'type': 'video_result',
            'recipient': data['recipient'],
            'answer': data['answer'],
        }))

    async def new_ice_candidate_handler(self, data):
        """
        Asynchronous method to handle new ICE candidate.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'new-ice-candidate',
                'recipient': self.scope['user'].id,
                'candidate': data['candidate'],
            }
        )

    async def new_ice_candidate(self, data):
        """
        Asynchronous method to send new ICE candidate.

        :param data: The event data.
        :type data: dict
        """
        await self.send(text_data=json.dumps({
            'type': 'new-ice-candidate',
            'recipient': data['recipient'],
            'candidate': data['candidate'],
        }))

    async def disconnect(self, code):
        """
        Asynchronous method to handle the disconnection event.
        Removes the connection from the channel layer.

        :param code: The code for the disconnection event.
        :type code: int
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def end_call_handler(self, data):
        """
        Asynchronous method to handle end of call.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'end_call',
                'reason': 'finished',
                'recipient': self.scope['user'].id,
            }
        )

    # Handler for the video_rejected message
    async def video_rejected_handler(self, data):
        """
        Asynchronous method to handle rejection of video call.

        :param data: The data received from the WebSocket.
        :type data: dict
        """
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'end_call',
                'reason': 'rejected',
                'recipient': data['recipient'],
            }
        )

    async def end_call(self, data):
        """
        Asynchronous method to send end of call message.

        :param data: The event data.
        :type data: dict
        """
        await self.send(text_data=json.dumps({
            'type': 'end_call',
            'reason': data['reason'],
            'recipient': data['recipient'],
        }))