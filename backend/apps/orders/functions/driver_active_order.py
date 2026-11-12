from apps.orders.models import Order


def driver_active_order(driver):
    """The order the driver is currently on (accepted / waiting / in progress), or None."""
    return Order.objects.filter(driver=driver, status__in=Order.DRIVER_ACTIVE_STATUSES).first()
