
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.orders.services import OrderService
from apps.drivers.models import Driver

class OrderActionView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, order_id):  # ← order_id qo'shildi
        action = request.data.get('action')
        driver_id = request.data.get('driver_id')

        if not driver_id:
            return Response({"error": "driver_id required."}, status=400)

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            return Response({"error": "Driver topilmadi."}, status=404)

        try:
            if action == "accept":
                OrderService.accept_order(order_id, driver)
            elif action == "arrive":
                OrderService.update_status(order_id, 'WAITING')
            elif action == "start":
                OrderService.update_status(order_id, 'IN_PROGRESS')
            elif action == "complete":
                OrderService.complete_order(order_id)
            elif action == "cancel":
                OrderService.cancel_by_driver(order_id, driver)
            else:
                return Response({"error": "Noto'g'ri action."}, status=400)

            return Response({"message": f"Muvaffaqiyatli: {action}"})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=400)
