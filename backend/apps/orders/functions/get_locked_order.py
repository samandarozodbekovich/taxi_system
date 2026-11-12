from apps.orders.models import Order


def get_locked_order(order_id):
    """Load the order with a row lock (call inside transaction.atomic())."""
    try:
        return Order.objects.select_for_update().get(id=order_id)
    except Order.DoesNotExist:
        raise ValueError("Order not found.")
