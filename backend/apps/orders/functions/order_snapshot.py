from apps.orders.models import Order


def order_snapshot(order_id):
    """
    The order's current state in the same shape as the order_update events. Sent when a
    WebSocket connects, so a client or driver that reconnects catches up on missed events.
    """
    order = Order.objects.select_related('driver').filter(id=order_id).first()
    if order is None:
        return None

    data = {'status': order.status}
    if order.driver and order.status in Order.DRIVER_ACTIVE_STATUSES:
        data.update({
            'driver_name': order.driver.full_name,
            'car_model': order.driver.car_model,
            'car_number': order.driver.car_number,
            'driver_phone': order.driver.phone_number,
        })
    if order.status == 'CANCELED':
        data.update({'cancel_by': order.cancel_by, 'cancel_reason': order.cancel_reason})
    return data
