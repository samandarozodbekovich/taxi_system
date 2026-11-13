from rest_framework import authentication, exceptions

from apps.drivers.functions import DRIVER_TOKEN_COOKIE, driver_from_token

# The driver panel sends this header with every request. A cookie is sent by the browser on
# its own, also for requests another site starts (CSRF), but another site can't add a custom
# header without a CORS preflight, which this server never allows.
PANEL_HEADER = "X-Requested-With"
PANEL_HEADER_VALUE = "driver-panel"
SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class DriverTokenAuthentication(authentication.BaseAuthentication):
    """
    The driver is resolved from the signed token, never from driver_id in the body/URL.
    The bot sends it as "Authorization: Bearer <token>"; the panel has it in an HttpOnly cookie.
    """
    keyword = "Bearer"

    def authenticate(self, request):
        parts = authentication.get_authorization_header(request).decode("latin-1").split()
        if parts and parts[0] == self.keyword:
            if len(parts) != 2:
                raise exceptions.AuthenticationFailed("Malformed token.")
            return (driver_from_token(parts[1]), parts[1])

        token = request.COOKIES.get(DRIVER_TOKEN_COOKIE)
        if not token:
            return None  # no token - the IsDriver permission returns 401
        if request.method not in SAFE_METHODS and request.headers.get(PANEL_HEADER) != PANEL_HEADER_VALUE:
            raise exceptions.PermissionDenied("Missing the driver panel header.")
        return (driver_from_token(token), token)

    def authenticate_header(self, request):
        # Without this DRF returns 403 instead of 401
        return self.keyword
