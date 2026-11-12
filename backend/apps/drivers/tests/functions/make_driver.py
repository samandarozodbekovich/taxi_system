from django.contrib.auth.hashers import make_password

from apps.drivers.models import Driver


def make_driver(code="DRV-TEST01", password="secret123", approved=True, **extra):
    fields = dict(
        driver_code=code,
        password_hash=make_password(password),
        full_name=f"Driver {code}",
        phone_number=f"+99890{code[-6:]}",
        car_model="Cobalt",
        car_color="White",
        car_number=f"01{code[-6:]}",
        is_approved=approved,
    )
    fields.update(extra)
    return Driver.objects.create(**fields)
