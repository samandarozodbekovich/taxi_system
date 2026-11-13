from django.db import transaction
from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.drivers.models import Driver

from .get_locked_order import get_locked_order
from .notify_order_update import notify_order_update


def cancel_by_operator(order_id, cancel_reason=None):
    """Cancel from the admin panel - the only way to cancel a trip that is already IN_PROGRESS."""
    with transaction.atomic():
        order = get_locked_order(order_id)
        order.transition_to("CANCELED")

        # Close offers nobody answered yet
        OrderDispatch.objects.filter(order=order, is_accepted=False, is_rejected=False).update(
            is_rejected=True, responded_at=timezone.now()
        )
        # The driver stays on the order for the record, but is free for new orders
        if order.driver_id:
            Driver.objects.filter(id=order.driver_id, status="BUSY").update(status="ONLINE", updated_at=timezone.now())

        order.canceled_at = timezone.now()
        order.cancel_by = "OPERATOR"
        if cancel_reason:
            order.cancel_reason = cancel_reason
        order.save()

        notify_order_update(order.id, {'status': 'CANCELED', 'cancel_by': 'OPERATOR', 'cancel_reason': cancel_reason})
        return order
