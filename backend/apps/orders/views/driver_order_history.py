from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.mixins import DriverAuthMixin
from apps.orders.models import Order
from apps.orders.serializers import OrderHistorySerializer

HISTORY_LIMIT = 10


class DriverOrderHistoryView(DriverAuthMixin, APIView):
    """The driver's latest trips."""

    def get(self, request):
        orders = Order.objects.filter(driver=request.user).order_by('-created_at')[:HISTORY_LIMIT]
        return Response(OrderHistorySerializer(orders, many=True).data)
