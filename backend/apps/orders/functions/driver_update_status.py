from django.db import transaction

from .get_locked_order import get_locked_order
from .update_status import update_status

# ACCEPTED -> WAITING ("I have arrived"), WAITING -> IN_PROGRESS ("Start trip")
DRIVER_SETTABLE_STATUSES = {'WAITING', 'IN_PROGRESS'}


def driver_update_status(order_id, driver, new_status):
    """Status change by the driver: only on their own order, in the allowed sequence."""
    if new_status not in DRIVER_SETTABLE_STATUSES:
        raise ValueError("Invalid status.")

    with transaction.atomic():
        order = get_locked_order(order_id)
        if order.driver_id != driver.id:
            raise ValueError("This order does not belong to you.")
        # Updated while holding the lock; update_status validates the transition
        return update_status(order_id, new_status)
