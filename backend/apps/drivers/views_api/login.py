from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.functions import create_driver_token, failed_login_attempts_key, login_source, record_failed_login
from apps.drivers.serializers import DriverLoginSerializer, DriverProfileSerializer
from apps.drivers.throttling import DriverLoginThrottle

# Failed attempts allowed per driver code from one source (Telegram user or IP). Counting per
# source, not per code alone, means a stranger who knows a driver's code can't lock the driver out.
MAX_FAILED_ATTEMPTS = 5
# Per driver code from all sources together - stops guessing spread over many IPs/accounts
MAX_FAILED_ATTEMPTS_PER_CODE = 50


class DriverLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    # Overall limit per source: settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['driver_login']
    throttle_classes = [DriverLoginThrottle]
    throttle_scope = 'driver_login'

    def post(self, request):
        driver_code = request.data.get('driver_code', '')
        fail_limits = {
            failed_login_attempts_key(driver_code, login_source(request)): MAX_FAILED_ATTEMPTS,
            failed_login_attempts_key(driver_code, 'any'): MAX_FAILED_ATTEMPTS_PER_CODE,
        }
        if any(cache.get(key, 0) >= limit for key, limit in fail_limits.items()):
            return Response(
                {"non_field_errors": ["Too many failed attempts. Please try again in 15 minutes."]},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        serializer = DriverLoginSerializer(data=request.data)
        if not serializer.is_valid():
            if not serializer.credentials_ok:
                for key in fail_limits:
                    record_failed_login(key)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cache.delete_many(list(fail_limits))
        driver = serializer.validated_data['driver']
        return Response({**DriverProfileSerializer(driver).data, 'token': create_driver_token(driver)})
