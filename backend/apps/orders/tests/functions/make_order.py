from django.contrib.gis.geos import Point

from apps.orders.models import Order


def make_order(client, status="SEARCHING", driver=None, **extra):
    return Order.objects.create(
        order_number=f"T-{Order.objects.count() + 1}-{client.id}",
        client=client,
        driver=driver,
        status=status,
        pickup_latitude=41.3,
        pickup_longitude=69.2,
        pickup_location=Point(69.2, 41.3, srid=4326),
        pickup_address="Point A",
        estimated_price=20000,
        **extra,
    )
