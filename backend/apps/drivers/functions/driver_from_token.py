from django.conf import settings
from django.core import signing
from rest_framework.exceptions import AuthenticationFailed

from apps.drivers.models import Driver

from .create_driver_token import TOKEN_MAX_AGE, TOKEN_SALT


def driver_from_token(token):
    """Verify the token and return the driver (shared by HTTP and WebSocket)."""
    try:
        payload = signing.loads(
            token, key=settings.DRIVER_TOKEN_SECRET_KEY, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE
        )
    except signing.SignatureExpired:
        raise AuthenticationFailed("Token has expired. Please log in again.")
    except signing.BadSignature:
        raise AuthenticationFailed("Invalid token.")

    driver = Driver.objects.filter(id=payload.get("driver_id")).first()
    if driver is None:
        raise AuthenticationFailed("Driver not found.")
    # Logged out / password changed since the token was issued
    if payload.get("v") != driver.token_version:
        raise AuthenticationFailed("Session has ended. Please log in again.")
    # Blocking or un-approving a driver invalidates their existing tokens immediately
    if driver.is_blocked:
        raise AuthenticationFailed("Your account is blocked.")
    if not driver.is_approved:
        raise AuthenticationFailed("Your account has not been approved by an admin yet.")
    return driver
