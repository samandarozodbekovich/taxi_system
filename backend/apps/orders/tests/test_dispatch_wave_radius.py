import sys
from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.dispatch.models import OrderDispatch
from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.tasks import dispatch_new_order

from .functions import make_client, make_order

DISPATCH_MODULE = sys.modules["apps.orders.functions.dispatch_order_to_drivers"]


@override_settings(CACHES=LOCMEM_CACHE)
@patch("apps.drivers.functions.notify_drivers_new_order")
@patch.object(DISPATCH_MODULE, "get_table_to", return_value=None)  # OSRM unavailable -> straight-line ETA
class DispatchWaveRadiusTests(TestCase):
    """An empty ring widens the search at once; only an empty city-wide search falls back to everyone."""

    def setUp(self):
        self.order = make_order(make_client(9401))  # pickup at 41.3, 69.2

    def driver_at(self, code, lat, lon, telegram_id):
        driver = make_driver(code, status="ONLINE", telegram_id=telegram_id)
        driver.update_location(lat, lon)
        return driver

    def offered_ids(self):
        return set(OrderDispatch.objects.filter(order=self.order).values_list("driver_id", flat=True))

    def test_empty_first_ring_widens_without_sending_city_wide(self, osrm, notify):
        near = self.driver_at("DRV-AAAAA1", 41.336, 69.2, 111)   # ~4 km: outside 3 km, inside 5 km
        self.driver_at("DRV-BBBBB2", 41.39, 69.2, 222)            # ~10 km

        dispatch_new_order(self.order.id)

        # Before the fix the empty 3 km ring sent the order to every online driver
        self.assertEqual(self.offered_ids(), {near.id})

    def test_falls_back_to_everyone_only_beyond_the_widest_radius(self, osrm, notify):
        far = self.driver_at("DRV-CCCCC3", 41.6, 69.2, 333)       # ~33 km

        dispatch_new_order(self.order.id)

        self.assertEqual(self.offered_ids(), {far.id})
