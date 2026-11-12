from .driver_active_order import driver_active_order
from .notify_order_update import notify_order_update


def notify_driver_location(driver, lat, lon):
    """Show the driver's position to the client of their active order (Mini App map)."""
    order = driver_active_order(driver)
    if order:
        notify_order_update(order.id, {'driver_location': {'lat': lat, 'lon': lon}})
