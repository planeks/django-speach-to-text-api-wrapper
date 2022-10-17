import asyncio

import azure.cognitiveservices.speech as speechsdk
from django.conf import settings

from api.stt_providers.base.base_stt import SttProvider


class MicrosoftProvider(SttProvider):
    transcript = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SERVICE_REGION,
            speech_recognition_language=self.language
        )
        self.stream = speechsdk.audio.PushAudioInputStream()
        self.audio_config = speechsdk.audio.AudioConfig(stream=self.stream)
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=self.audio_config
        )
        self.speech_recognizer.recognizing.connect(self.save_transcript)

    async def run_transcription_process(self):
        """Runs transcription process in a background"""

        async def _run_transcription_process():
            self.speech_recognizer.start_continuous_recognition()

        asyncio.ensure_future(_run_transcription_process())

    async def transcribe_stream(self, bytes_stream):
        """Writes bytes stream to the PushAudioInputStream of Azure API"""

        self.stream.write(bytes_stream)

    def save_transcript(self, event):
        self.transcript = event.result.text
