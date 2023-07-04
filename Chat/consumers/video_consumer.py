from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .utils import is_valid_match


class VideoConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = None

    async def connect(self):
        self.room_group_name = f"video_{self.scope['user'].id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
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
        except KeyError:
            return

    async def video_offer_handler(self, data):
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'video_offer',
                'recipient': self.scope['user'].id,
                'offer': data['offer'],
            }
        )

    async def video_offer(self, data):
        await self.send(text_data=json.dumps({
            'type': 'video_offer',
            'recipient': data['recipient'],
            'offer': data['offer'],
        }))

    async def video_answer_handler(self, data):
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'video_result',
                'recipient': self.scope['user'].id,
                'answer': data['answer'],
            }
        )

    async def video_result(self, data):
        await self.send(text_data=json.dumps({
            'type': 'video_result',
            'recipient': data['recipient'],
            'answer': data['answer'],
        }))

    async def new_ice_candidate_handler(self, data):
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'new-ice-candidate',
                'recipient': self.scope['user'].id,
                'candidate': data['candidate'],
            }
        )

    async def new_ice_candidate(self, data):
        await self.send(text_data=json.dumps({
            'type': 'new-ice-candidate',
            'recipient': data['recipient'],
            'candidate': data['candidate'],
        }))

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
        text_data_json = json.loads(text_data)

        try:
            match text_data_json['type']:
                case 'end_call':
                    await self.end_call_handler(text_data_json)
                case 'end_call_confirmed':
                    await self.end_call_confirmed_handler(text_data_json)
                # Handle other types of messages...
        except KeyError:
            return

    async def end_call_handler(self, data):
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'end_call',
                'recipient': self.scope['user'].id,
            }
        )

    async def end_call_confirmed_handler(self, data):
        await self.channel_layer.group_send(
            f"video_{data['recipient']}",
            {
                'type': 'end_call_confirmed',
                'recipient': self.scope['user'].id,
            }
        )

    async def end_call(self, data):
        await self.send(text_data=json.dumps({
            'type': 'end_call',
            'recipient': data['recipient'],
        }))

    async def end_call_confirmed(self, data):
        await self.send(text_data=json.dumps({
            'type': 'end_call_confirmed',
            'recipient': data['recipient'],
        }))
