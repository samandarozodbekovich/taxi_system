from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.orders.models import Order

class OrderDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"error": "Topilmadi."}, status=404)

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