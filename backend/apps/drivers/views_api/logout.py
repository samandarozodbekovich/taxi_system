from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.functions import revoke_driver_tokens
from apps.drivers.mixins import DriverAuthMixin


class DriverLogoutView(DriverAuthMixin, APIView):
    """Log out everywhere: the bot and the panel both have to log in again."""

    def post(self, request):
        revoke_driver_tokens([request.user.id])
        return Response({"message": "Logged out."})
