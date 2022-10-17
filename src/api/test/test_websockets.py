import datetime
import json

from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from rest_framework.authtoken.models import Token

from accounts.models import User
from api.consumers import TranscriptionConsumer
from api.middleware import STTMiddleware


class SocketBaseTestCase(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user('test@gmail.com', 'Test User', '12121212')
        self.token = Token.objects.create(user=self.user).key
        self.input_data = json.dumps({
            'action': 'transcribe',
            'request_id': datetime.datetime.now().isoformat(),
            'voice_stream': ''
        })


class STTWebsocketAccessibilityTests(SocketBaseTestCase):
    def setUp(self):
        super(STTWebsocketAccessibilityTests, self).setUp()

    async def test_valid_token_access(self):
        communicator = WebsocketCommunicator(
            STTMiddleware(TranscriptionConsumer.as_asgi()),
            f"/ws/transcription/?token={self.token}"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_to(text_data=self.input_data)
        response = json.loads(await communicator.receive_from())
        self.assertEqual(response['response_status'], 200)
        self.assertEqual(json.loads(response['data']),
                         {'language': 'en-US', 'stt_provider': 'google', 'transcript': None})
        self.assertEqual(response['action'], 'transcribe')

        await communicator.disconnect()

    async def test_invalid_token_access(self):
        communicator = WebsocketCommunicator(
            STTMiddleware(TranscriptionConsumer.as_asgi()),
            f"/ws/transcription/?token={self.token + 'error'}"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_to(text_data=self.input_data)
        response = json.loads(await communicator.receive_from())
        self.assertEqual(response['response_status'], 403)
        self.assertIsNone(response['data'])
        self.assertEqual(response['action'], 'transcribe')

        await communicator.disconnect()


class STTProviderBaseTest(SocketBaseTestCase):
    provider = None

    async def _test_provider_response(self):
        communicator = WebsocketCommunicator(
            STTMiddleware(TranscriptionConsumer.as_asgi()),
            f"/ws/transcription/?token={self.token}&stt_provider={self.provider}&language=en-US"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_to(text_data=self.input_data)
        response = json.loads(await communicator.receive_from())
        self.assertEqual(response['response_status'], 200)
        self.assertEqual(
            json.loads(response['data']),
            {
                'language': 'en-US',
                'stt_provider': self.provider,
                'transcript': None
            }
        )
        self.assertEqual(response['action'], 'transcribe')

        await communicator.disconnect()


class GoogleSttTests(STTProviderBaseTest):
    def setUp(self):
        super(GoogleSttTests, self).setUp()
        self.provider = 'google'

    async def test_google_provider_response(self):
        return await self._test_provider_response()


class MicrosoftSttTests(STTProviderBaseTest):
    def setUp(self):
        super(MicrosoftSttTests, self).setUp()
        self.provider = 'microsoft'

    async def test_microsoft_provider_response(self):
        return await self._test_provider_response()


class DeepgramSttTests(STTProviderBaseTest):
    def setUp(self):
        super(DeepgramSttTests, self).setUp()
        self.provider = 'deepgram'

    async def test_deepgram_provider_response(self):
        return await self._test_provider_response()


class AmazonSttTests(STTProviderBaseTest):
    def setUp(self):
        super(AmazonSttTests, self).setUp()
        self.provider = 'amazon'

    async def test_amazon_provider_response(self):
        return await self._test_provider_response()
