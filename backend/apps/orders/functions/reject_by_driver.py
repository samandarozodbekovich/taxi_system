from django.db import transaction
from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.orders.models import Order

from .has_open_offers import has_open_offers
from .schedule_dispatch import schedule_dispatch


def reject_by_driver(order_id, driver):
    """The driver rejected the offer or it timed out - mark the dispatch as rejected."""
    with transaction.atomic():
        updated = OrderDispatch.objects.filter(
            order_id=order_id, driver=driver, is_accepted=False
        ).update(is_rejected=True, responded_at=timezone.now())

        # Everyone in this wave said no - don't wait for the offers to expire, send the next wave now
        if updated and not has_open_offers(order_id) and Order.objects.filter(id=order_id, status="SEARCHING").exists():
            schedule_dispatch(order_id)
    return updated > 0
