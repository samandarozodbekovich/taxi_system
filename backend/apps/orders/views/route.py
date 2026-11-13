from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.clients.mixins import ClientAuthMixin
from apps.orders.functions import calculate_estimate_price
from services import get_route


class RouteInfoView(ClientAuthMixin, APIView):
    # Only Mini App clients, and rate-limited per client - otherwise anyone could use our OSRM server for free
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'route'

    def post(self, request):
        try:
            coords = {key: float(request.data.get(key)) for key in ('start_lat', 'start_lon', 'end_lat', 'end_lon')}
        except (TypeError, ValueError):
            return Response({"status": "error", "message": "Invalid route coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        route_info = get_route(**coords)
        if route_info.get("status") != "success":
            return Response(route_info, status=status.HTTP_400_BAD_REQUEST)

        # Price is computed on the server so the price shown to the client matches the order price
        route_info["estimated_price"] = int(calculate_estimate_price(route_info["distance_km"]))
        return Response(route_info)
