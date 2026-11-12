import uuid

from django.contrib.gis.geos import Point
from django.db import transaction

from apps.orders.models import Order

from .calculate_estimate_price import calculate_estimate_price
from .calculate_trip_route import calculate_trip_route
from .order_number_for import order_number_for
from .schedule_dispatch import schedule_dispatch
from .schedule_search_timeout import schedule_search_timeout


def create_order(client, pickup_lat, pickup_lon, destination_lat=None, destination_lon=None,
                 pickup_address="", destination_address=""):
    distance = 0
    destination_point = None
    route_line = None

    if destination_lat and destination_lon:
        destination_point = Point(float(destination_lon), float(destination_lat), srid=4326)
        distance, route_line = calculate_trip_route(pickup_lat, pickup_lon, destination_lat, destination_lon)
        distance = round(distance, 2)

    estimated_price = calculate_estimate_price(distance)

    # order_number is derived from the id, which doesn't exist yet: create with a temporary unique
    # value and replace it in the same transaction, so the temporary value is never visible
    with transaction.atomic():
        order = Order.objects.create(
            order_number=uuid.uuid4().hex,
            client=client,
            pickup_location=Point(float(pickup_lon), float(pickup_lat), srid=4326),
            pickup_latitude=pickup_lat,
            pickup_longitude=pickup_lon,
            pickup_address=pickup_address,
            destination_location=destination_point,
            destination_latitude=destination_lat,
            destination_longitude=destination_lon,
            destination_address=destination_address,
            distance_km=distance,
            total_distance=distance,
            route_geometry=route_line,
            estimated_price=estimated_price,
            total_price=estimated_price,
            status='SEARCHING'
        )
        order.order_number = order_number_for(order.id)
        order.save(update_fields=['order_number'])
        schedule_search_timeout(order.id)
        # Driver search (OSRM) and Telegram messages run in Celery - the request returns 201 immediately
        schedule_dispatch(order.id)

    return order
