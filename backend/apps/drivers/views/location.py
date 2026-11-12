from rest_framework.views import APIView
from rest_framework.response import Response

from apps.drivers.mixins import DriverAuthMixin
from apps.orders.functions import notify_driver_location


class DriverLocationUpdateView(DriverAuthMixin, APIView):

    def post(self, request, pk):
        # The driver comes from the token - another driver's location cannot be changed
        driver = request.user
        if driver.id != pk:
            return Response({"error": "You can only send your own location."}, status=403)

        try:
            lat = float(request.data.get("latitude"))
            lon = float(request.data.get("longitude"))
        except (TypeError, ValueError):
            return Response({"error": "latitude and longitude are required."}, status=400)

        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return Response({"error": "Invalid coordinates."}, status=400)

        # Updates current_latitude, current_longitude and current_location (PointField)
        driver.update_location(lat, lon)
        # The client of the active order sees the driver approaching on the map
        notify_driver_location(driver, lat, lon)

        return Response({"success": True})
