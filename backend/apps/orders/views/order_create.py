from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from ..models import Order
from ..serializers import OrderCreateSerializer
from ...drivers.service import notify_drivers_new_order

class OrderCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        client_tg_id = request.data.get('client_telegram_id')
        if not client_tg_id:
            return Response({"error": "client_telegram_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        active_order_exists = Order.objects.filter(
            client__telegram_id=client_tg_id,
            status__in=['SEARCHING', 'ACCEPTED', 'WAITING', 'IN_PROGRESS']
        ).exists()
        
        if active_order_exists:
            return Response(
                {"error": "You already have an active order. Please complete or cancel it before creating a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()
            notify_drivers_new_order(order) 
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)