import abc


class SttProvider(abc.ABC):
    """Base speech-to-text provider class"""

    def __init__(self, language='en-US'):
        self.language = language

    @abc.abstractmethod
    async def run_transcription_process(self):
        """
        Runs transcription process as a background task. Used to perform initial run of API client data processing.

        Example:
            Run worker in new thread.
        """
        pass

    @abc.abstractmethod
    async def transcribe_stream(self, bytes_stream):
        """Adds stream of bytes to the transcription process

        Args:
            bytes_stream: stream of bytes
        """
        pass
