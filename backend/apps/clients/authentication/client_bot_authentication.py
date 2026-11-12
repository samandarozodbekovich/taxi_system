from rest_framework import authentication, exceptions

from apps.clients.functions import bot_secret_is_valid, get_registered_client


class ClientBotAuthentication(authentication.BaseAuthentication):
    """
    Server-to-server request from the client bot (X-Bot-Secret header). Only then is
    client_telegram_id from the body/query trusted - the bot took it from Telegram.
    """

    def authenticate(self, request):
        if "X-Bot-Secret" not in request.headers:
            return None
        if not bot_secret_is_valid(request):
            raise exceptions.AuthenticationFailed("Invalid bot secret.")

        telegram_id = request.data.get("client_telegram_id") or request.query_params.get("client_telegram_id")
        try:
            telegram_id = int(telegram_id)
        except (TypeError, ValueError):
            raise exceptions.AuthenticationFailed("client_telegram_id is required.")
        return (get_registered_client(telegram_id), None)
