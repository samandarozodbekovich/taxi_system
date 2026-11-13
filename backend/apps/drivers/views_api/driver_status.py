from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.drivers.mixins import DriverAuthMixin
from apps.drivers.models import Driver
from apps.orders.functions import driver_active_order


class DriverStatusView(DriverAuthMixin, APIView):

    def post(self, request, pk):
        # The driver comes from the token; the pk in the URL may only be their own
        if request.user.id != pk:
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

        with transaction.atomic():
            # Same lock as accept_order - the status can't change while an order is being accepted
            driver = Driver.objects.select_for_update().get(id=pk)
            # A driver on a trip stays BUSY: going ONLINE mid-trip would put them back into
            # dispatch and let them accept a second order
            if driver_active_order(driver) is not None:
                return Response(
                    {"error": "You have an active order. Finish or cancel it first.", "status": driver.status},
                    status=status.HTTP_409_CONFLICT
                )

            new_status = "ONLINE" if is_online else "OFFLINE"
            driver.status = new_status
            driver.save(update_fields=["status", "updated_at"])

        return Response(
            {"status": new_status},
            status=status.HTTP_200_OK
        )
