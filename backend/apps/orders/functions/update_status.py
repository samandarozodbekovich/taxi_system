from django.db import transaction
from django.utils import timezone

from .get_locked_order import get_locked_order
from .notify_order_update import notify_order_update

# Timestamp field set when the order enters a status
STATUS_TIMESTAMP_FIELDS = {'WAITING': 'arrived_at', 'IN_PROGRESS': 'started_at'}


def update_status(order_id, new_status, extra_data=None):
    """Change the status (validated by Order.transition_to) and push it over WebSocket."""
    with transaction.atomic():
        order = get_locked_order(order_id)
        order.transition_to(new_status)
        if new_status in STATUS_TIMESTAMP_FIELDS:
            setattr(order, STATUS_TIMESTAMP_FIELDS[new_status], timezone.now())
        order.save()

        notify_order_update(order.id, {'status': new_status, **(extra_data or {})})
        return order
