from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.functions import DRIVER_TOKEN_COOKIE, revoke_driver_tokens
from apps.drivers.mixins import DriverAuthMixin


class DriverLogoutView(DriverAuthMixin, APIView):
    """Log out everywhere: the bot and the panel both have to log in again."""

    def post(self, request):
        revoke_driver_tokens([request.user.id])
        response = Response({"message": "Logged out."})
        # Same SameSite as when it was set, or the browser keeps the cookie
        response.delete_cookie(DRIVER_TOKEN_COOKIE, path="/", samesite="None" if request.is_secure() else "Lax")
        return response
