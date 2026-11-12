from django.utils import timezone

from apps.dispatch.models import OrderDispatch


def is_offered_to_driver(order, driver):
    """True if the order was offered to this driver and the offer is still open."""
    return OrderDispatch.objects.filter(
        order=order, driver=driver, is_rejected=False, expires_at__gt=timezone.now()
    ).exists()
