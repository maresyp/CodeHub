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
                case 'video-offer':
                    await self.video_offer_handler(text_data_json)
                case 'video-answer':
                    await self.video_answer_handler(text_data_json)
                case 'new-ice-candidate':
                    await self.new_ice_candidate_handler(text_data_json)
        except KeyError:
            return

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
