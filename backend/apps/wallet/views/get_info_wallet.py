from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models import DriverWallet
from ..serializers import GetInfoWalletSerializer
from ...drivers.models import Driver


class InfoWalletView(APIView):
    
    def get(self, request):
        telegram_id = request.query_params.get("telegram_id")
        
        if not telegram_id:
            return Response(
                {"error": "telegram_id required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            driver = Driver.objects.get(
                telegram_id=telegram_id
            )
            
            wallet = DriverWallet.objects.get(
                driver = driver
            )
        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = GetInfoWalletSerializer(wallet)
        return Response(serializer.data)