from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.orders.models import Order
from apps.drivers.mixins import DriverAuthMixin


class OrderDetailView(DriverAuthMixin, APIView):
    """Order details (client address) for the driver panel - authenticated drivers only."""

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"error": "Not found."}, status=404)

        # Don't show details of an order accepted by another driver
        if order.driver_id is not None and order.driver_id != request.user.id:
            return Response({"error": "This order belongs to another driver."}, status=403)

        # The driver has seen the offer (is_viewed was never filled in before)
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
