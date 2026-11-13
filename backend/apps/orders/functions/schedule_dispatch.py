from django.db import transaction

from apps.orders.tasks import dispatch_new_order


def schedule_dispatch(order_id, countdown=0):
    """Send the next wave of offers (find drivers, Telegram messages) - in Celery, after commit."""
    transaction.on_commit(lambda: dispatch_new_order.apply_async(args=[order_id], countdown=countdown), robust=True)
