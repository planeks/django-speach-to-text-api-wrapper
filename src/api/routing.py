from django.urls import re_path

from api.consumers import TranscriptionConsumer

ws_urlpatterns = [
    re_path(r'ws/transcription/', TranscriptionConsumer.as_asgi()),
]