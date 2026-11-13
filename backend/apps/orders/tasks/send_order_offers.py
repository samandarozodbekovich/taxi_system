from celery import shared_task

from apps.dispatch.models import OrderDispatch
from apps.drivers.models import Driver
from apps.orders.models import Order


@shared_task(name="apps.orders.tasks.send_order_offers")
def send_order_offers(order_id, driver_ids):
    """Telegram messages about an order to one batch of drivers (see send_order_offers_in_batches)."""
    # drivers.functions is imported lazily, like in dispatch_new_order
    from apps.drivers.functions import notify_drivers_new_order

    order = Order.objects.filter(id=order_id).first()
    # A later batch may run after the order was taken - don't send a dead offer
    if order is None or order.status != "SEARCHING":
        return f"Order {order_id}: not searching, offers not sent."

    # Only drivers whose offer is still open (not rejected meanwhile)
    open_ids = OrderDispatch.objects.filter(
        order_id=order_id, driver_id__in=driver_ids, is_accepted=False, is_rejected=False
    ).values_list("driver_id", flat=True)
    drivers = list(Driver.objects.filter(id__in=open_ids))
    notify_drivers_new_order(order, drivers)
    return f"Order {order_id}: offer sent to {len(drivers)} driver(s)."
