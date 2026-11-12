from rest_framework import authentication, exceptions

from apps.drivers.functions import driver_from_token


class DriverTokenAuthentication(authentication.BaseAuthentication):
    """The driver is resolved from the signed token, never from driver_id in the body/URL."""
    keyword = "Bearer"

    def authenticate(self, request):
        parts = authentication.get_authorization_header(request).decode("latin-1").split()
        if not parts or parts[0] != self.keyword:
            return None  # no token - the IsDriver permission returns 401
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed("Malformed token.")
        return (driver_from_token(parts[1]), parts[1])

    def authenticate_header(self, request):
        # Without this DRF returns 403 instead of 401
        return self.keyword
