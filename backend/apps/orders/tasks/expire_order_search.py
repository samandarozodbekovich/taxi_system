from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.orders.models import Order

# Celery ETA fires slightly late, never exactly on time - a small margin
DEADLINE_TOLERANCE_SECONDS = 5


@shared_task(name="apps.orders.tasks.expire_order_search")
def expire_order_search(order_id, timeout_seconds):
    """
    The search timed out: if nobody accepted, the order becomes NO_DRIVER and the client
    sees "No driver found" in the Mini App. Scheduled by schedule_search_timeout.
    """
    # orders.functions imports this task - import lazily to avoid a circular import
    from apps.orders.functions import notify_order_update

    deadline = timezone.now() - timedelta(seconds=timeout_seconds - DEADLINE_TOLERANCE_SECONDS)

    with transaction.atomic():
        # Conditional UPDATE: no-op if a driver accepted, the client canceled,
        # or the search restarted meanwhile (searching_started_at changed)
        updated = Order.objects.filter(
            id=order_id, status="SEARCHING", searching_started_at__lte=deadline,
        ).update(status="NO_DRIVER", updated_at=timezone.now())

        if not updated:
            return f"Order {order_id}: search still running or already finished."

        # Close the offers of drivers who didn't answer
        OrderDispatch.objects.filter(
            order_id=order_id, is_accepted=False, is_rejected=False
        ).update(is_rejected=True, responded_at=timezone.now())

        notify_order_update(order_id, {"status": "NO_DRIVER"})

    return f"Order {order_id}: no driver found (NO_DRIVER)."
