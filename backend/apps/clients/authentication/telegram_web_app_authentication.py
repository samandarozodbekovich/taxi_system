from rest_framework import authentication, exceptions

from apps.clients.functions import client_from_init_data


class TelegramWebAppAuthentication(authentication.BaseAuthentication):
    """Mini App: the raw initData comes in the "Authorization: tma <initData>" header."""
    keyword = "tma"

    def authenticate(self, request):
        parts = authentication.get_authorization_header(request).decode("utf-8", "replace").split(" ", 1)
        if parts[0] != self.keyword:
            return None
        if len(parts) != 2 or not parts[1]:
            raise exceptions.AuthenticationFailed("initData was not sent.")
        return (client_from_init_data(parts[1]), None)

    def authenticate_header(self, request):
        # Without this DRF returns 403 instead of 401
        return self.keyword
