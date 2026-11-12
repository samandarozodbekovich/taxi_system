from apps.clients.authentication import ClientBotAuthentication, TelegramWebAppAuthentication
from apps.clients.permissions import IsClient


class ClientAuthMixin:
    """For client endpoints: access with Mini App initData or the client bot secret."""
    authentication_classes = [TelegramWebAppAuthentication, ClientBotAuthentication]
    permission_classes = [IsClient]
