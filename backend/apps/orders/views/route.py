from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from services.yandex_maps import RoutingService


class RouteInfoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            start_lat = float(request.data.get('start_lat'))
            start_lon = float(request.data.get('start_lon'))
            end_lat = float(request.data.get('end_lat'))
            end_lon = float(request.data.get('end_lon'))
        except (TypeError, ValueError):
            return Response({"status": "error", "message": "Invalid route coordinates."}, status=status.HTTP_400_BAD_REQUEST)

        route_info = RoutingService.get_route(
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon
        )

        if route_info.get("status") != "success":
            return Response(route_info, status=status.HTTP_400_BAD_REQUEST)

        return Response(route_info)
