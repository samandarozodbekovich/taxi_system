from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.mixins import ClientAuthMixin
from apps.orders.models import Order
from apps.orders.serializers import OrderHistorySerializer

HISTORY_LIMIT = 10


class OrderHistoryByClientView(ClientAuthMixin, APIView):
    """The client's latest orders (Mini App initData or client bot)."""

    def get(self, request):
        orders = Order.objects.filter(client=request.user).order_by('-created_at')[:HISTORY_LIMIT]
        return Response(OrderHistorySerializer(orders, many=True).data)
