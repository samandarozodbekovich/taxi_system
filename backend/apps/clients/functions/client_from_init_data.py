from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import AuthenticationFailed

from .get_registered_client import get_registered_client
from .verify_telegram_init_data import verify_telegram_init_data


def client_from_init_data(init_data):
    """Verify initData and return the client (shared by HTTP and WebSocket)."""
    if not settings.CLIENT_BOT_TOKEN:
        raise ImproperlyConfigured("CLIENT_BOT_TOKEN is not set in .env.")

    try:
        user = verify_telegram_init_data(init_data, settings.CLIENT_BOT_TOKEN)
    except ValueError as e:
        raise AuthenticationFailed(str(e))
    return get_registered_client(user["id"])
