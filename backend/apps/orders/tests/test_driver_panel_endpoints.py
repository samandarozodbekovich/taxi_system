from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import auth_header, make_driver

from .functions import make_client, make_dispatch, make_order


@override_settings(CACHES=LOCMEM_CACHE)
class DriverPanelEndpointsTests(TestCase):

    def setUp(self):
        self.api = APIClient()
        self.driver = make_driver("DRV-AAAAA1", status="ONLINE")
        self.headers = auth_header(self.driver)

    def test_active_order_is_restored(self):
        order = make_order(make_client(9001), "WAITING", self.driver)
        response = self.api.get("/api/orders/driver/active/", **self.headers)
        self.assertEqual((response.data["active"], response.data["id"], response.data["status"]),
                         (True, order.id, "WAITING"))

    def test_no_active_order(self):
        make_order(make_client(9002), "COMPLETED", self.driver)
        self.assertFalse(self.api.get("/api/orders/driver/active/", **self.headers).data["active"])

    def test_history_shows_only_own_trips(self):
        own = make_order(make_client(9003), "COMPLETED", self.driver)
        make_order(make_client(9004), "COMPLETED", make_driver("DRV-BBBBB2"))
        response = self.api.get("/api/orders/driver/history/", **self.headers)
        self.assertEqual([o["id"] for o in response.data], [own.id])

    def test_available_orders_lists_open_offers(self):
        order = make_order(make_client(9005))
        make_dispatch(order, self.driver)
        response = self.api.get("/api/orders/available/", **self.headers)
        self.assertEqual([o["id"] for o in response.data], [order.id])

    def send_location(self):
        with self.captureOnCommitCallbacks(execute=False) as callbacks:
            response = self.api.post(f"/api/drivers/{self.driver.id}/location/",
                                     {"latitude": 41.31, "longitude": 69.24}, format="json", **self.headers)
        self.assertEqual(response.status_code, 200)
        return callbacks

    def test_location_is_pushed_to_client_of_active_order(self):
        make_order(make_client(9006), "ACCEPTED", self.driver)
        self.assertEqual(len(self.send_location()), 1)  # one WebSocket update scheduled

    def test_location_without_active_order_is_not_pushed(self):
        self.assertEqual(len(self.send_location()), 0)
