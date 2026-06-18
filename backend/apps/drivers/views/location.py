from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from apps.drivers.models import Driver


@method_decorator(csrf_exempt, name='dispatch')
class DriverLocationUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            driver = Driver.objects.get(id=pk)
        except Driver.DoesNotExist:
            return Response({"error": "Driver topilmadi."}, status=404)

        lat = request.data.get("latitude")
        lon = request.data.get("longitude")

        if not lat or not lon:
            return Response({"error": "latitude va longitude kerak."}, status=400)

        # Driver modelidagi update_location metodini chaqiramiz
        # U current_latitude, current_longitude va current_location (PointField) ni yangilaydi
        driver.update_location(lat, lon)

        return Response({"success": True})