from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.db import close_old_connections
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(token):
    """Retrieves user instance for given token"""

    try:
        user = Token.objects.get(key=token).user
    except Token.DoesNotExist:
        user = None
    return user


class TokenAuthMiddleware(BaseMiddleware):
    """
    Middleware that retrieves auth token from query sting during connection to the websocket

    Example:
        .../?token=auth_token
    """

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None
        scope['user'] = await get_user(token_key)
        return await super().__call__(scope, receive, send)


class SttProviderMiddleware(BaseMiddleware):
    """
    Middleware that retrieves speech-to-text provider name from query sting during connection to the websocket

    Example:
        .../?stt_provider=provider_name
    """

    async def __call__(self, scope, receive, send):
        try:
            provider = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('stt_provider', None)
        except ValueError:
            provider = None
        if provider: scope['stt_provider'] = provider
        return await super().__call__(scope, receive, send)


class LanguageCodeMiddleware(BaseMiddleware):
    """
    Middleware that retrieves language code from query sting during connection to the websocket

    Example:
        .../?language=language_code
    """

    async def __call__(self, scope, receive, send):
        try:
            language = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('language', None)
        except ValueError:
            language = None
        if language: scope['language'] = language
        return await super().__call__(scope, receive, send)


def STTMiddleware(callable):
    """Combines all given middleware in single function as a pipeline"""

    return LanguageCodeMiddleware(SttProviderMiddleware(TokenAuthMiddleware(callable)))
