import sys
from unittest.mock import patch

from django.db import connection
from django.test import TestCase, override_settings

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.functions import dispatch_order_to_drivers

from .functions import make_client, make_order

# The package re-exports the function under the module's name - patch the module itself
DISPATCH_MODULE = sys.modules["apps.orders.functions.dispatch_order_to_drivers"]


@override_settings(CACHES=LOCMEM_CACHE)
@patch.object(DISPATCH_MODULE, "get_table_to", return_value=None)  # OSRM unavailable -> straight-line ETA
class DispatchOrderToDriversTests(TestCase):
    """Nearest-driver search (ST_DWithin on geography) honours the wave radius."""

    def setUp(self):
        self.order = make_order(make_client(9201))  # pickup at 41.3, 69.2

    def driver_at(self, code, lat, lon):
        driver = make_driver(code, status="ONLINE")
        driver.update_location(lat, lon)
        return driver

    def test_only_drivers_within_radius(self, osrm):
        near = self.driver_at("DRV-AAAAA1", 41.31, 69.2)   # ~1.1 km
        self.driver_at("DRV-BBBBB2", 41.39, 69.2)          # ~10 km

        dispatches = dispatch_order_to_drivers(self.order, radius_km=3)

        self.assertEqual([d.driver_id for d in dispatches], [near.id])
        self.assertAlmostEqual(float(dispatches[0].distance_to_client_km), 1.1, delta=0.1)

    def test_wider_radius_reaches_further_drivers(self, osrm):
        self.driver_at("DRV-BBBBB2", 41.39, 69.2)
        self.assertEqual(len(dispatch_order_to_drivers(self.order, radius_km=12)), 1)

    def test_location_column_is_geography_with_spatial_index(self, osrm):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT indexdef FROM pg_indexes WHERE tablename = 'drivers_driver' AND indexdef ILIKE '%%gist%%'"
            )
            indexes = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT udt_name FROM information_schema.columns "
                           "WHERE table_name = 'drivers_driver' AND column_name = 'current_location'")
            column_type = cursor.fetchone()[0]
        self.assertEqual(column_type, "geography")
        self.assertTrue(any("current_location" in index for index in indexes))
