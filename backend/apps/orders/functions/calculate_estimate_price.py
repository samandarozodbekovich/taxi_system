from decimal import Decimal

from apps.settings_app.models import SystemSetting

from .calculate_waiting_price import calculate_waiting_price


def calculate_estimate_price(distance_km, waiting_time_minutes=0):
    base_fare = Decimal(SystemSetting.get_setting("MIN_PRICE", 5000))
    per_km_rate = Decimal(SystemSetting.get_setting("PRICE_PER_KM", 2000))

    price = base_fare + per_km_rate * Decimal(str(distance_km)) + calculate_waiting_price(waiting_time_minutes)

    # Round to 100 sum (as a plain number, not Decimal('1.2E+4'))
    return (price / 100).quantize(Decimal('1')) * 100
