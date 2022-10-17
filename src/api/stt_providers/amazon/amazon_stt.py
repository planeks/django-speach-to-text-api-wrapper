import asyncio

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.exceptions import BadRequestException
from amazon_transcribe.handlers import TranscriptResultStreamHandler

from api.stt_providers.base.base_stt import SttProvider
from api.stt_providers.base.utils import split_stream_by_chunks


class AmazonTranscriptionHandler(TranscriptResultStreamHandler):
    transcript = None

    async def handle_transcript_event(self, transcript_event):
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                self.transcript = alt.transcript


class AmazonSttProvider(SttProvider):
    stream = None
    handler = None
    max_chunk_size = 4096

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = []
        self.client = TranscribeStreamingClient(region="us-west-2")

    async def run_transcription_process(self):
        """Runs transcription process in a background"""

        async def _run_transcription_process():
            """Initializes transcription stream and assigns output stream to the handler"""

            self.stream = await self.client.start_stream_transcription(
                language_code=self.language,
                media_sample_rate_hz=16000,
                media_encoding="pcm",
            )
            self.handler = AmazonTranscriptionHandler(self.stream.output_stream)
            try:
                await asyncio.gather(self.handler.handle_events())
            except BadRequestException:
                pass

        asyncio.ensure_future(_run_transcription_process())

    async def transcribe_stream(self, bytes_stream):
        """
        Pushes bytes stream to the transcription input stream
        Additional split of the input stream required, to avoid excess of amazon limits
        """

        chunks = split_stream_by_chunks(bytes_stream, self.max_chunk_size)
        if self.stream:
            chunks.extend(self.buffer)
            for chunk in chunks:
                await self.stream.input_stream.send_audio_event(audio_chunk=chunk)
            self.buffer = []
        else:
            self.buffer.extend(chunks)

    @property
    def transcript(self):
        return self.handler.transcript if self.handler else None
