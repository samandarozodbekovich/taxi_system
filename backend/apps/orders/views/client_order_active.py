from rest_framework.views import APIView
from rest_framework.response import Response

from apps.clients.mixins import ClientAuthMixin
from apps.orders.models import Order

class ActiveOrderByClientView(ClientAuthMixin, APIView):

    def get(self, request):
        # The client is resolved from signed initData, not from client_telegram_id in the query
        client = request.user

        order = Order.objects.filter(client=client, status__in=Order.ACTIVE_STATUSES).order_by('-created_at').first()

        if not order:
            return Response({"active": False})

        data = {
            'active': True,
            'id': order.id,
            'status': order.status,
        }
        return Response(data)