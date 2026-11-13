from django.db import transaction
from django.utils import timezone

from apps.dispatch.models import OrderDispatch

from .get_locked_order import get_locked_order
from .notify_order_update import notify_order_update
from .schedule_dispatch import schedule_dispatch
from .schedule_search_timeout import schedule_search_timeout


def cancel_by_driver(order_id, driver):
    """The driver drops the order: it goes back to SEARCHING and is offered to other drivers."""
    with transaction.atomic():
        order = get_locked_order(order_id)
        if order.driver_id is None or order.driver_id != driver.id:
            raise ValueError("You are not allowed to cancel this order.")
        if not order.can_transition_to("SEARCHING"):
            raise ValueError("The order has not been accepted yet or is already finished.")

        # A rejected record (created even if the driver had no dispatch) keeps this
        # order from being offered to the same driver again
        OrderDispatch.objects.update_or_create(
            order=order,
            driver=driver,
            defaults={"is_accepted": False, "is_rejected": True, "responded_at": timezone.now()},
        )

        order.driver = None
        order.transition_to("SEARCHING")
        order.accepted_at = None
        # The search timeout restarts from now (an older timeout task won't touch this order)
        order.searching_started_at = timezone.now()
        # The new search starts again from the smallest radius
        order.dispatch_wave = 0
        order.save()
        schedule_search_timeout(order.id)
        schedule_dispatch(order.id)

        driver.status = "ONLINE"
        driver.save(update_fields=['status', 'updated_at'])

        notify_order_update(order.id, {'status': 'SEARCHING', 'cancel_by': 'DRIVER'})
        return order
