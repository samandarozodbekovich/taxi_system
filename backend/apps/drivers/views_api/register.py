from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..serializers import DriverRegisterSerializer

class DriverRegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        serializer = DriverRegisterSerializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()
        
            return Response({
                "message": "Ro'yxatdan muvaffaqiyatli o'tdingiz!",
                "id": driver.id,
                "driver_code": driver.driver_code,  # ← driver shu kodni eslab qoladi
                "full_name": driver.full_name,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        