from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..serializers import DriverLoginSerializer, DriverProfileSerializer


class DriverLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        serializer = DriverLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            driver = serializer.validated_data['driver']
            
            return Response(
                DriverProfileSerializer(driver).data,
                status=status.HTTP_200_OK
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            