from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.tests.constants import LOCMEM_CACHE

ROUTE = {"start_lat": 41.3, "start_lon": 69.2, "end_lat": 41.31, "end_lon": 69.25}


@override_settings(CACHES=LOCMEM_CACHE)
class RouteAuthTests(TestCase):
    """The route preview calls our OSRM server - it must not be an open proxy."""

    def test_route_without_init_data_is_401(self):
        response = APIClient().post("/api/orders/route/", ROUTE, format="json")
        self.assertEqual(response.status_code, 401)
