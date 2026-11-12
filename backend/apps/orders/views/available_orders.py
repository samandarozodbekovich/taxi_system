from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from ...dispatch.models import OrderDispatch
from apps.drivers.mixins import DriverAuthMixin
from ..serializers.driver_order_list import DriverOrderListSerializer


class AvailableOrdersView(DriverAuthMixin, APIView):

    def get(self, request):
        # Previously checked the non-existent request.driver_profile - the endpoint never worked
        driver = request.user

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
