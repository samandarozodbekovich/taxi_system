from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from ..models import Driver


class DriverStatusView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            driver = Driver.objects.get(id=pk)
        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )

        if driver.is_blocked:
            return Response(
                {"error": "Sizning hisobingiz bloklangan."},
                status=status.HTTP_403_FORBIDDEN
            )

        is_online = request.data.get("is_online")

        if is_online is None:
            return Response(
                {"error": "is_online maydoni talab qilinadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = "ONLINE" if is_online else "OFFLINE"
        driver.status = new_status
        driver.save(update_fields=["status", "updated_at"]) 

        return Response(
            {"status": new_status},
            status=status.HTTP_200_OK
        )