from decimal import Decimal

from apps.settings_app.models import SystemSetting


def calculate_waiting_price(waiting_minutes):
    """Charge for the time the driver waited beyond the free waiting time."""
    per_minute_rate = Decimal(SystemSetting.get_setting("WAITING_PRICE_PER_MINUTE", 500))
    free_waiting_time = Decimal(SystemSetting.get_setting("FREE_WAITING_TIME", 3))
    paid_minutes = Decimal(str(waiting_minutes)) - free_waiting_time
    return (per_minute_rate * paid_minutes).quantize(Decimal('1')) if paid_minutes > 0 else Decimal(0)
