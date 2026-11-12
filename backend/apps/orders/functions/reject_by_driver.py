from django.utils import timezone

from apps.dispatch.models import OrderDispatch


def reject_by_driver(order_id, driver):
    """The driver rejected the offer or it timed out - mark the dispatch as rejected."""
    updated = OrderDispatch.objects.filter(
        order_id=order_id, driver=driver, is_accepted=False
    ).update(is_rejected=True, responded_at=timezone.now())
    return updated > 0
