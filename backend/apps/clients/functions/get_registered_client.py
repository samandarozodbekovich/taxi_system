from rest_framework.exceptions import AuthenticationFailed

from apps.clients.models import Client


def get_registered_client(telegram_id):
    try:
        return Client.objects.get(telegram_id=telegram_id)
    except Client.DoesNotExist:
        raise AuthenticationFailed("Please register in the bot first (/start).")
