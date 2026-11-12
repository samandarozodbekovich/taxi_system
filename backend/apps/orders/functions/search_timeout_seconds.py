from apps.settings_app.models import SystemSetting

# If nobody accepts within this time the order becomes NO_DRIVER.
# Configurable from the admin panel: SystemSetting ORDER_SEARCH_TIMEOUT_SECONDS
DEFAULT_SEARCH_TIMEOUT_SECONDS = 180


def search_timeout_seconds():
    try:
        return int(SystemSetting.get_setting("ORDER_SEARCH_TIMEOUT_SECONDS", DEFAULT_SEARCH_TIMEOUT_SECONDS))
    except (TypeError, ValueError):
        return DEFAULT_SEARCH_TIMEOUT_SECONDS
