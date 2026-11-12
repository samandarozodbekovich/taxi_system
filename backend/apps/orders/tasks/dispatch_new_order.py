from celery import shared_task

from apps.orders.models import Order


@shared_task(name="apps.orders.tasks.dispatch_new_order")
def dispatch_new_order(order_id):
    """Find the nearest drivers (PostGIS + OSRM) and send them a Telegram message."""
    # orders.functions imports this task - import lazily to avoid a circular import
    from apps.drivers.functions import notify_drivers_new_order
    from apps.orders.functions import dispatch_order_to_all_online, dispatch_order_to_drivers

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return f"Order {order_id} not found."

    if order.status != "SEARCHING":
        return f"Order {order_id} is not searching ({order.status})."

    # Nobody nearby (e.g. driver locations unknown) - offer it to every online driver
    dispatches = dispatch_order_to_drivers(order) or dispatch_order_to_all_online(order)
    notify_drivers_new_order(order, [d.driver for d in dispatches])
    return f"Order {order_id}: offered to {len(dispatches)} driver(s)."
