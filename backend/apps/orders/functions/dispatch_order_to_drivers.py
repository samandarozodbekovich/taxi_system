from datetime import timedelta

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.utils import timezone

from apps.dispatch.models import OrderDispatch
from apps.drivers.models import Driver
from services import get_table_to

from .search_timeout_seconds import search_timeout_seconds

SEARCH_RADIUS_KM = 5
MAX_DRIVERS = 5
AVERAGE_SPEED_KMH = 40


def dispatch_order_to_drivers(order):
    """Offer the order to the nearest drivers, sorted by real road ETA. Returns the new dispatches."""
    # Drivers this order was already offered to (unique_together('order', 'driver'))
    offered_driver_ids = OrderDispatch.objects.filter(order=order).values_list('driver_id', flat=True)

    drivers = list(
        Driver.objects.filter(status="ONLINE", is_blocked=False, is_approved=True, wallet__gte=0)
        .exclude(id__in=offered_driver_ids)
        .filter(current_location__distance_lte=(order.pickup_location, D(km=SEARCH_RADIUS_KM)))
        .annotate(air_distance=Distance('current_location', order.pickup_location))
        .order_by('air_distance')[:MAX_DRIVERS]
    )

    # Road travel time for all drivers in ONE OSRM table request
    routes = get_table_to(
        [(d.current_location.y, d.current_location.x) for d in drivers],
        order.pickup_location.y, order.pickup_location.x,
    ) or [None] * len(drivers)

    candidates = []
    for driver, route in zip(drivers, routes):
        if route:
            distance, eta = route["distance_km"], route["duration_minutes"]
        else:
            # OSRM unavailable or no route - straight-line distance from PostGIS
            distance = driver.air_distance.km
            eta = distance / AVERAGE_SPEED_KMH * 60
        candidates.append((eta, distance, driver))
    candidates.sort(key=lambda c: c[0])

    expires_at = timezone.now() + timedelta(seconds=search_timeout_seconds())
    dispatches = []
    for _, distance, driver in candidates:
        # get_or_create: a concurrent dispatch may have created this driver meanwhile
        dispatch, created = OrderDispatch.objects.get_or_create(
            order=order,
            driver=driver,
            defaults={"distance_to_client_km": distance, "is_sent": True, "expires_at": expires_at},
        )
        if created:
            dispatches.append(dispatch)
    return dispatches
