import secrets

from apps.drivers.models import Driver

# No confusable characters (0/O, 1/I/L) - 31^6 ≈ 900 million combinations
DRIVER_CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"


def generate_driver_code():
    while True:
        code = "DRV-" + "".join(secrets.choice(DRIVER_CODE_ALPHABET) for _ in range(6))
        if not Driver.objects.filter(driver_code=code).exists():
            return code
