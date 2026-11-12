from django.db import transaction
from django.utils import timezone

from .calculate_waiting_price import calculate_waiting_price
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
        if new_status == 'IN_PROGRESS' and order.arrived_at:
            # The trip starts - charge for the time the driver waited for the client
            waited_minutes = (order.started_at - order.arrived_at).total_seconds() / 60
            order.waiting_price = calculate_waiting_price(waited_minutes)
        order.save()

        notify_order_update(order.id, {'status': new_status, **(extra_data or {})})
        return order
