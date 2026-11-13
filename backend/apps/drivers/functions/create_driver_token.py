from django.conf import settings
from django.core import signing

# The token is signed with DRIVER_TOKEN_SECRET_KEY (not shared with Channels), so it cannot be forged
TOKEN_SALT = "apps.drivers.auth-token"
TOKEN_MAX_AGE = 60 * 60 * 24 * 30  # 30 days


def create_driver_token(driver):
    """Token issued on login; sent back as "Authorization: Bearer <token>"."""
    # "v" ties the token to the current token_version - bumping it revokes the token
    return signing.dumps({"driver_id": driver.id, "v": driver.token_version}, key=settings.DRIVER_TOKEN_SECRET_KEY, salt=TOKEN_SALT)
