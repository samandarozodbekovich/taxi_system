from apps.settings_app.models import SystemSetting

# How long one driver has to answer an offer; after that the next wave of drivers gets it.
# Used for OrderDispatch.expires_at and the driver panel timer, so both agree.
# Configurable from the admin panel: SystemSetting DRIVER_OFFER_TIMEOUT_SECONDS
DEFAULT_OFFER_TIMEOUT_SECONDS = 45


def offer_timeout_seconds():
    try:
        return int(SystemSetting.get_setting("DRIVER_OFFER_TIMEOUT_SECONDS", DEFAULT_OFFER_TIMEOUT_SECONDS))
    except (TypeError, ValueError):
        return DEFAULT_OFFER_TIMEOUT_SECONDS
