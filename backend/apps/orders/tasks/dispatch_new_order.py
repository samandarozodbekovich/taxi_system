from celery import shared_task
from django.db import transaction

from apps.orders.models import Order

# Celery countdown may fire a moment before the offers expire - start the next wave a bit later
NEXT_WAVE_MARGIN_SECONDS = 1


@shared_task(name="apps.orders.tasks.dispatch_new_order")
def dispatch_new_order(order_id):
    """
    Send the next wave of offers: the nearest drivers not offered yet (PostGIS + OSRM),
    each wave with a wider radius. Runs when the order is created, when every driver of the
    previous wave rejected, and when the previous wave's offers expired (scheduled below).
    """
    # orders.functions imports this task - import lazily to avoid a circular import
    from apps.orders.functions import (
        dispatch_order_to_all_online, dispatch_order_to_drivers, has_open_offers,
        offer_timeout_seconds, schedule_dispatch, send_order_offers_in_batches,
    )
    from apps.orders.functions.dispatch_order_to_drivers import WAVE_RADII_KM

    with transaction.atomic():
        # The lock serializes concurrent runs (a rejection and the expiry timer at once)
        order = Order.objects.select_for_update().filter(id=order_id).first()
        if order is None:
            return f"Order {order_id} not found."
        if order.status != "SEARCHING":
            return f"Order {order_id} is not searching ({order.status})."
        # Another run already sent this wave - its own timer continues the chain
        if has_open_offers(order_id):
            return f"Order {order_id}: the current wave is still open."

        order.dispatch_wave += 1
        order.save(update_fields=["dispatch_wave", "updated_at"])
        radius_km = WAVE_RADII_KM[min(order.dispatch_wave, len(WAVE_RADII_KM)) - 1]

        # Nobody nearby (e.g. driver locations unknown) - offer it to every online driver
        dispatches = dispatch_order_to_drivers(order, radius_km) or dispatch_order_to_all_online(order)
        # Next wave when these offers expire; stops once the order leaves SEARCHING
        # (accepted, canceled, or NO_DRIVER from expire_order_search)
        schedule_dispatch(order_id, countdown=offer_timeout_seconds() + NEXT_WAVE_MARGIN_SECONDS)

    # Telegram is slow - send after the lock is released
    send_order_offers_in_batches(order_id, [d.driver_id for d in dispatches])
    return f"Order {order_id}: wave {order.dispatch_wave}, offered to {len(dispatches)} driver(s)."
