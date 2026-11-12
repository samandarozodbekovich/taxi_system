from decimal import Decimal

from apps.settings_app.models import SystemSetting


def calculate_waiting_price(waiting_minutes):
    """Charge for the full minutes the driver waited beyond the free waiting time."""
    per_minute_rate = Decimal(SystemSetting.get_setting("WAITING_PRICE_PER_MINUTE", 500))
    free_waiting_time = int(SystemSetting.get_setting("FREE_WAITING_TIME", 3))
    # Only full minutes are charged (10 min 59 s -> 10 min)
    paid_minutes = int(waiting_minutes) - free_waiting_time
    return per_minute_rate * paid_minutes if paid_minutes > 0 else Decimal(0)
