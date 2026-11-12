from rest_framework.exceptions import AuthenticationFailed

from apps.clients.functions import client_from_init_data
from apps.drivers.functions import driver_from_token
from apps.orders.models import Order


def is_order_participant(order_id, init_data=None, token=None):
    """True if initData belongs to the order's client or the token to its assigned driver."""
    try:
        order = Order.objects.only('client_id', 'driver_id').get(id=order_id)
    except Order.DoesNotExist:
        return False

    try:
        if init_data:
            return order.client_id == client_from_init_data(init_data).id
        if token:
            return order.driver_id is not None and order.driver_id == driver_from_token(token).id
    except AuthenticationFailed:
        return False
    return False
