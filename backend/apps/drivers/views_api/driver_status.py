from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.drivers.mixins import DriverAuthMixin


class DriverStatusView(DriverAuthMixin, APIView):

    def post(self, request, pk):
        # The driver comes from the token; the pk in the URL may only be their own
        driver = request.user
        if driver.id != pk:
            return Response(
                {"error": "You can only change your own status."},
                status=status.HTTP_403_FORBIDDEN
            )

        is_online = request.data.get("is_online")

        if not isinstance(is_online, bool):
            return Response(
                {"error": "The is_online field (true/false) is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = "ONLINE" if is_online else "OFFLINE"
        driver.status = new_status
        driver.save(update_fields=["status", "updated_at"])

        return Response(
            {"status": new_status},
            status=status.HTTP_200_OK
        )
