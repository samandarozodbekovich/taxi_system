from django.db import transaction
from django.utils import timezone

from apps.dispatch.models import OrderDispatch

from .get_locked_order import get_locked_order
from .notify_order_update import notify_order_update


def cancel_by_client(order_id, client, cancel_reason=None):
    with transaction.atomic():
        order = get_locked_order(order_id)
        if order.client != client:
            raise ValueError("You are not allowed to cancel this order.")
        # IN_PROGRESS -> CANCELED is left to the operator (see Order.ALLOWED_TRANSITIONS)
        if order.status == "IN_PROGRESS":
            raise ValueError("The trip has already started. Contact support to cancel it.")
        if not order.can_transition_to("CANCELED"):
            raise ValueError("The order is already finished or canceled.")

        if order.status == "SEARCHING":
            OrderDispatch.objects.filter(order=order).update(
                is_accepted=False, is_rejected=True, responded_at=timezone.now()
            )

        if order.driver:
            order.driver.status = "ONLINE"
            order.driver.save(update_fields=['status', 'updated_at'])
            order.driver = None

        order.transition_to("CANCELED")
        order.canceled_at = timezone.now()
        order.cancel_by = "CLIENT"
        if cancel_reason:
            order.cancel_reason = cancel_reason
        order.save()

        notify_order_update(order.id, {'status': 'CANCELED', 'cancel_by': 'CLIENT', 'cancel_reason': cancel_reason})
        return order
