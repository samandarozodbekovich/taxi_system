from decimal import Decimal

from apps.settings_app.models import SystemSetting


def calculate_estimate_price(distance_km, waiting_time_minutes=0):
    base_fare = Decimal(SystemSetting.get_setting("MIN_PRICE", 5000))
    per_km_rate = Decimal(SystemSetting.get_setting("PRICE_PER_KM", 2000))
    per_minute_rate = Decimal(SystemSetting.get_setting("WAITING_PRICE_PER_MINUTE", 500))
    free_waiting_time = Decimal(SystemSetting.get_setting("FREE_WAITING_TIME", 3))

    price = base_fare + (per_km_rate * Decimal(str(distance_km)))

    if waiting_time_minutes > free_waiting_time:
        price += per_minute_rate * Decimal(waiting_time_minutes - free_waiting_time)

    # Round to 100 sum (as a plain number, not Decimal('1.2E+4'))
    return (price / 100).quantize(Decimal('1')) * 100
