from django.db import transaction
from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.orders.models import Order

from .has_open_offers import has_open_offers
from .schedule_dispatch import schedule_dispatch


def reject_by_driver(order_id, driver):
    """The driver rejected the offer or it timed out - mark the dispatch as rejected."""
    with transaction.atomic():
        # Lock the order first, like every other order function. Without it two drivers who
        # reject at the same moment each still see the other's offer as open (neither update
        # is committed yet), so neither starts the next wave and the client waits for the timer.
        order = Order.objects.select_for_update().filter(id=order_id).first()

        updated = OrderDispatch.objects.filter(
            order_id=order_id, driver=driver, is_accepted=False
        ).update(is_rejected=True, responded_at=timezone.now())

        # Everyone in this wave said no - don't wait for the offers to expire, send the next wave now
        if updated and order is not None and order.status == "SEARCHING" and not has_open_offers(order_id):
            schedule_dispatch(order_id)
    return updated > 0
