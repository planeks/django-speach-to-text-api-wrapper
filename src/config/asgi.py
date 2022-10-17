import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from api.middleware import STTMiddleware
from api.routing import ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': STTMiddleware(URLRouter(ws_urlpatterns))
})
