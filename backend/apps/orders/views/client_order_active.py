from datetime import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.clients.models import Client
from apps.orders.models import Order

class ActiveOrderByClientView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        telegram_id = request.query_params.get('client_telegram_id')
        if not telegram_id:
            return Response({"error": "client_telegram_id is required."}, status=400)

        try:
            client = Client.objects.get(telegram_id=telegram_id)
        except Client.DoesNotExist:
            return Response({"error": "Bunday mijoz topilmadi."}, status=404)

        # Active statuses: SEARCHING, ACCEPTED, WAITING, IN_PROGRESS
        active_statuses = ['SEARCHING', 'ACCEPTED', 'WAITING', 'IN_PROGRESS']
        order = Order.objects.filter(client=client, status__in=active_statuses).order_by('-created_at').first()

        if not order:
            return Response({"active": False})

        data = {
            'active': True,
            'id': order.id,
            'status': order.status,
        }
        return Response(data)