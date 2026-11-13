from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..permissions import IsDriverBot
from ..serializers import DriverRegisterSerializer

class DriverRegisterView(APIView):
    authentication_classes = []
    # Only the driver bot registers drivers: it takes telegram_id from the Telegram update,
    # so nobody can register with someone else's Telegram id (it receives the order messages)
    permission_classes = [IsDriverBot]

    def post(self, request):

        serializer = DriverRegisterSerializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()

            # No token is issued: the driver logs in after an admin approves the account
            return Response({
                "message": "You are registered! You can log in once an admin approves your account.",
                "id": driver.id,
                "driver_code": driver.driver_code,  # the driver needs to remember this code
                "full_name": driver.full_name,
                "is_approved": driver.is_approved,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
