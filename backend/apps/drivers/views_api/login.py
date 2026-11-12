from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.drivers.functions import create_driver_token, failed_login_attempts_key, record_failed_login
from apps.drivers.serializers import DriverLoginSerializer, DriverProfileSerializer

# Consecutive failed attempts allowed per driver code (protects against password guessing)
MAX_FAILED_ATTEMPTS = 5


class DriverLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    # Overall per-IP limit: settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['driver_login']
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'driver_login'

    def post(self, request):
        fail_key = failed_login_attempts_key(request.data.get('driver_code', ''))
        if cache.get(fail_key, 0) >= MAX_FAILED_ATTEMPTS:
            return Response(
                {"non_field_errors": ["Too many failed attempts. Please try again in 15 minutes."]},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = DriverLoginSerializer(data=request.data)
        if not serializer.is_valid():
            if not serializer.credentials_ok:
                record_failed_login(fail_key)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(fail_key)
        driver = serializer.validated_data['driver']
        return Response({**DriverProfileSerializer(driver).data, 'token': create_driver_token(driver)})
