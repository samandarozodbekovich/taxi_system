from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.mixins import DriverAuthMixin
from apps.orders.functions import driver_active_order


class DriverActiveOrderView(DriverAuthMixin, APIView):
    """The driver's current order - lets the panel restore it after a reload."""

    def get(self, request):
        order = driver_active_order(request.user)
        if order is None:
            return Response({"active": False})
        return Response({
            "active": True,
            "id": order.id,
            "status": order.status,
            "pickup_address": order.pickup_address,
            "destination_address": order.destination_address,
            "pickup_latitude": float(order.pickup_latitude or 0),
            "pickup_longitude": float(order.pickup_longitude or 0),
        })
