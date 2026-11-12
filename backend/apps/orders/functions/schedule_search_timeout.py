from django.db import transaction

from apps.orders.tasks import expire_order_search

from .search_timeout_seconds import search_timeout_seconds


def schedule_search_timeout(order_id):
    """
    Mark the order NO_DRIVER when the search times out (Celery, after commit).
    robust=True - if Redis/Celery is down the order is still created and the error is logged.
    """
    timeout = search_timeout_seconds()
    transaction.on_commit(
        lambda: expire_order_search.apply_async(args=[order_id, timeout], countdown=timeout),
        robust=True,
    )
