from django.urls import re_path
from .consumers.chat_consumer import ChatConsumer
from .consumers.video_consumer import VideoConsumer

websocket_urlpatterns = [
    re_path(r'ws/socket-server/chat', ChatConsumer.as_asgi()),
    re_path(r'ws/socket-server/video', VideoConsumer.as_asgi()),
]
