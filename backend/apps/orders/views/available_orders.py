from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...dispatch.models import OrderDispatch
from ..serializers.driver_order_list import DriverOrderListSerializer


class AvailableOrdersView(APIView): 
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request, 'driver_profile'):
            return Response({"error": "You are not the driver."}, status=403)

        driver = request.driver_profile
        
        if driver.status != 'ONLINE':
            return Response({"error": "Your driver profile is not online. Please contact support."}, status=403)
        
        dispatches = OrderDispatch.objects.filter(
            driver=driver,
            is_accepted=False,
            is_rejected=False,
            expires_at__gt=timezone.now()
        ).select_related('order', "order__client")

        available_orders = [d.order for d in dispatches]
        serializer = DriverOrderListSerializer(available_orders, many=True)
        return Response(serializer.data, status=200)    
