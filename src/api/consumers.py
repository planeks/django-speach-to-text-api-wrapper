import base64
import json

from djangochannelsrestframework.consumers import AsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.permissions import IsAuthenticated
from rest_framework import status

from api.stt_providers import AVAILABLE_PROVIDERS


class TranscriptionConsumer(AsyncAPIConsumer):
    permission_classes = [IsAuthenticated]

    async def websocket_connect(self, message):
        """
        Called when connection to websocket is initiated.
        Initializes speech-to-text provider and runs transcription process background job.
        """

        self.user = self.scope.get('user')
        self.stt_provider = self.scope.get('stt_provider')
        self.language = self.scope.get('language')
        self.provider_class = AVAILABLE_PROVIDERS.get(self.stt_provider)
        self.provider = self.provider_class(self.language)
        await self.provider.run_transcription_process()
        await super().websocket_connect(message)

    @action()
    async def transcribe(self, voice_stream, **kwargs):
        """
        Called when websocket receives message.

        Args:
            voice_stream: base64 encoded audio stream
        Returns:
            Response with provided transcription, language and provider name
        """

        bytes_stream = base64.b64decode(voice_stream)
        if bytes_stream: await self.provider.transcribe_stream(bytes_stream)
        transcript = self.provider.transcript
        return {
            'language': self.language,
            'stt_provider': self.stt_provider,
            'transcript': transcript
        }, status.HTTP_200_OK
