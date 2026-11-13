from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.mixins import DriverAuthMixin
from apps.drivers.serializers import DriverProfileSerializer


class DriverMeView(DriverAuthMixin, APIView):
    """The driver's current profile and status - the bot reads it instead of trusting its own copy."""

    def get(self, request):
        return Response(DriverProfileSerializer(request.user).data)
