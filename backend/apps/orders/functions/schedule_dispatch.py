from django.db import transaction

from apps.orders.tasks import dispatch_new_order


def schedule_dispatch(order_id):
    """Find drivers and send them Telegram messages - in Celery, after commit."""
    transaction.on_commit(lambda: dispatch_new_order.delay(order_id), robust=True)
