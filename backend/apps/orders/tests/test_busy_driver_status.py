from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.models import Driver
from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import auth_header, make_driver

from .functions import make_client, make_dispatch, make_order


@override_settings(CACHES=LOCMEM_CACHE)
class BusyDriverStatusTests(TestCase):
    """A driver on a trip can't go ONLINE/OFFLINE and can't accept a second order."""

    def setUp(self):
        self.api = APIClient()
        self.driver = make_driver("DRV-AAAAA1", status="BUSY")
        self.trip = make_order(make_client(7001), "IN_PROGRESS", self.driver)

    def set_status(self, is_online):
        return self.api.post(
            f"/api/drivers/{self.driver.id}/status/", {"is_online": is_online}, format="json", **auth_header(self.driver)
        )

    def test_busy_driver_cannot_go_online_or_offline(self):
        for is_online in (False, True):
            self.assertEqual(self.set_status(is_online).status_code, 409)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, "BUSY")

    def test_driver_can_go_online_after_trip(self):
        self.trip.status = "COMPLETED"
        self.trip.save()
        self.assertEqual(self.set_status(True).status_code, 200)

    def test_driver_with_active_order_cannot_accept_another(self):
        # Status out of sync with the orders (e.g. changed in the admin) - the active order still blocks
        Driver.objects.filter(id=self.driver.id).update(status="ONLINE")
        second = make_order(make_client(7002))
        make_dispatch(second, self.driver)
        response = self.api.post(
            f"/api/orders/{second.id}/action/", {"action": "accept"}, format="json", **auth_header(self.driver)
        )
        self.assertEqual(response.status_code, 400)
        second.refresh_from_db()
        self.assertEqual(second.status, "SEARCHING")
