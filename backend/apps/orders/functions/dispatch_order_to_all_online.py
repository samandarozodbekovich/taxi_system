from datetime import timedelta

from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.drivers.models import Driver

from .search_timeout_seconds import search_timeout_seconds


def dispatch_order_to_all_online(order):
    """
    Fallback when no driver is nearby (e.g. locations unknown): offer the order to every
    ONLINE driver reachable on Telegram that hasn't been offered it yet. Returns the new dispatches.
    """
    offered_driver_ids = OrderDispatch.objects.filter(order=order).values_list('driver_id', flat=True)
    drivers = Driver.objects.filter(
        status="ONLINE", is_blocked=False, is_approved=True,
        wallet_record__balance__gte=0, telegram_id__isnull=False,
    ).exclude(id__in=offered_driver_ids)

    expires_at = timezone.now() + timedelta(seconds=search_timeout_seconds())
    dispatches = []
    for driver in drivers:
        dispatch, created = OrderDispatch.objects.get_or_create(
            order=order, driver=driver, defaults={"is_sent": True, "expires_at": expires_at},
        )
        if created:
            dispatches.append(dispatch)
    return dispatches
