import queue
import threading

from google.api_core.exceptions import OutOfRange
from google.cloud import speech

from api.stt_providers.base.base_stt import SttProvider


class GoogleSttProvider(SttProvider):
    transcript = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.language
        )
        self.streaming_config = speech.StreamingRecognitionConfig(config=self.config, interim_results=True)
        self.buffer = queue.Queue()

    async def run_transcription_process(self):
        """Runs transcription process in new thread"""

        def _run_transcription_process():
            """Initializes async request and responses"""

            try:
                requests = (speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in self.chunks_generator())
                responses = self.client.streaming_recognize(requests=requests, config=self.streaming_config)
                self.response_loop(responses)
            except OutOfRange:
                # Exception is raised in case, when there is no input byte stream
                return

        self.thread = threading.Thread(target=_run_transcription_process).start()

    def chunks_generator(self):
        """Generates chunks of data retrieved from self.buffer which is used as a queue"""

        while True:
            chunk = self.buffer.get()
            yield chunk

    async def transcribe_stream(self, bytes_stream):
        """Adds bytes stream to the buffer queue"""

        self.buffer.put(bytes_stream)

    def response_loop(self, responses):
        """Saves retrieved transcription from Google API"""

        for response in responses:
            for result in response.results:
                alternatives = result.alternatives
                for alternative in alternatives:
                    self.transcript = alternative.transcript
