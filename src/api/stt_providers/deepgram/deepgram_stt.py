from deepgram import Deepgram
from django.conf import settings

from api.stt_providers.base.base_stt import SttProvider


class DeepgramSttProvider(SttProvider):
    transcript = None
    socket = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Deepgram(settings.DEEPGRAM_API_KEY)
        self.buffer = []

    async def run_transcription_process(self):
        """Initialize websocket to Deepgram and registers handler with callback to save the response from Deepgram"""

        try:
            self.socket = await self.client.transcription.live({
                'encoding': 'linear16',
                'punctuate': True,
                'interim_results': True,
                'sample_rate': 16000,
                'channels': 1,
                'language': self.language
            })
            self.socket.registerHandler(self.socket.event.TRANSCRIPT_RECEIVED, self.save_transcript)
        except Exception as ex:
            pass

    async def transcribe_stream(self, bytes_stream):
        """Sends bytes stream to Deepgram websocket"""

        self.socket.send(bytes_stream)

    async def save_transcript(self, data):
        """Callback which is used to save transcribed response"""

        if data.get('channel') and data.get('is_final'):
            self.transcript = data['channel']['alternatives'][0]['transcript'] or self.transcript
