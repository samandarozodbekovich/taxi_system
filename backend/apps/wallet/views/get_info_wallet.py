from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models import DriverWallet
from ..serializers import GetInfoWalletSerializer
from apps.drivers.mixins import DriverAuthMixin


class InfoWalletView(DriverAuthMixin, APIView):
    
    def get(self, request):
        # The driver is resolved from the token, not from telegram_id in the query
        driver = request.user

        try:
            wallet = DriverWallet.objects.get(driver=driver)
        except DriverWallet.DoesNotExist:
            # Previously this case caused a 500 error
            return Response(
                {"error": "Wallet not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = GetInfoWalletSerializer(wallet)
        return Response(serializer.data)
