from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.dispatch.models import OrderDispatch
from apps.drivers.mixins import DriverAuthMixin
from apps.orders.functions import is_offered_to_driver
from apps.orders.models import Order


class OrderDetailView(DriverAuthMixin, APIView):
    """Order details (client address) for the driver panel - only for its driver or a driver it was offered to."""

    def get(self, request, pk):
        order = Order.objects.filter(id=pk).first()
        if order is None:
            return Response({"error": "Not found."}, status=404)

        if order.driver_id is not None and order.driver_id != request.user.id:
            return Response({"error": "This order belongs to another driver."}, status=403)
        if order.driver_id is None and not is_offered_to_driver(order, request.user):
            return Response({"error": "This order was not offered to you."}, status=403)

        # The driver has seen the offer
        OrderDispatch.objects.filter(order=order, driver=request.user, is_viewed=False).update(
            is_viewed=True, viewed_at=timezone.now()
        )

        return Response({
            "id": order.id,
            "pickup_address": order.pickup_address,
            "destination_address": order.destination_address,
            "distance_km": float(order.distance_km or 0),
            "estimated_price": float(order.estimated_price or 0),
            "pickup_latitude": float(order.pickup_latitude or 0),
            "pickup_longitude": float(order.pickup_longitude or 0),
            "status": order.status
        })
