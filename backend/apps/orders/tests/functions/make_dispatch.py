from datetime import timedelta

from django.utils import timezone

from apps.dispatch.models import OrderDispatch


def make_dispatch(order, driver, expires_in_seconds=180, **extra):
    return OrderDispatch.objects.create(
        order=order, driver=driver, expires_at=timezone.now() + timedelta(seconds=expires_in_seconds), **extra
    )
