from api.stt_providers.amazon.amazon_stt import AmazonSttProvider
from api.stt_providers.deepgram.deepgram_stt import DeepgramSttProvider
from api.stt_providers.google.google_stt import GoogleSttProvider
from api.stt_providers.microsoft.microsoft_stt import MicrosoftProvider
from decouple import config


class ProvidersRepository:
    def __init__(self):
        self.available_providers = {}
        self.add_providers()

    def add_providers(self):
        self.add_google_provider()
        self.add_deepgram_provider()
        self.add_amazon_provider()
        self.add_microsoft_provider()

    def add_google_provider(self):
        if config('GOOGLE_APPLICATION_CREDENTIALS', default=''):
            self.available_providers['google'] = GoogleSttProvider

    def add_deepgram_provider(self):
        if config('DEEPGRAM_API_KEY', default=''):
            self.available_providers['deepgram'] = DeepgramSttProvider

    def add_amazon_provider(self):
        if config('AWS_ACCESS_KEY_ID', default='') and config('AWS_SECRET_ACCESS_KEY', default=''):
            self.available_providers['amazon'] = AmazonSttProvider

    def add_microsoft_provider(self):
        if config('AZURE_SPEECH_KEY', default='') and config('AZURE_SERVICE_REGION', default=''):
            self.available_providers['microsoft'] = MicrosoftProvider

AVAILABLE_PROVIDERS = ProvidersRepository().available_providers
