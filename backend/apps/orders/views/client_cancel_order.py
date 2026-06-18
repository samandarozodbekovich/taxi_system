
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.clients.models import Client
from apps.orders.services import OrderService



class OrderCancelByClientView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, order_id):
        telegram_id = request.data.get('client_telegram_id')
        cancel_reason = request.data.get('cancel_reason')

        if not telegram_id:
            return Response({"error": "client_telegram_id is required."}, status=400)

        try:
            client = Client.objects.get(telegram_id=telegram_id)
        except Client.DoesNotExist:
            return Response({"error": "Bunday mijoz topilmadi."}, status=404)

        try:
            OrderService.cancel_by_client(order_id, client, cancel_reason)
            return Response({"message": "Buyurtma muvaffaqiyatli bekor qilindi."})
        except Exception as e:
            return Response({"error": str(e)}, status=400)