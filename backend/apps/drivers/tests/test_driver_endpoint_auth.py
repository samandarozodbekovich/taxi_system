from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.models import Driver

from .constants import LOCMEM_CACHE
from .functions import auth_header, make_driver


@override_settings(CACHES=LOCMEM_CACHE)
class DriverEndpointAuthTests(TestCase):

    def setUp(self):
        self.api = APIClient()
        self.driver = make_driver("DRV-AAAAA1")
        self.other = make_driver("DRV-BBBBB2")

    def set_status(self, driver_id, **headers):
        return self.api.post(f"/api/drivers/{driver_id}/status/", {"is_online": True}, format="json", **headers)

    def test_status_without_token_is_401(self):
        self.assertEqual(self.set_status(self.driver.id).status_code, 401)

    def test_cannot_change_other_drivers_status(self):
        self.assertEqual(self.set_status(self.other.id, **auth_header(self.driver)).status_code, 403)
        self.other.refresh_from_db()
        self.assertEqual(self.other.status, "OFFLINE")

    def test_me_returns_current_status(self):
        Driver.objects.filter(id=self.driver.id).update(status="ONLINE")  # e.g. changed in the panel
        response = self.api.get("/api/drivers/me/", **auth_header(self.driver))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.driver.id)
        self.assertTrue(response.data["is_online"])

    def test_cannot_update_other_drivers_location(self):
        response = self.api.post(
            f"/api/drivers/{self.other.id}/location/", {"latitude": 41.3, "longitude": 69.2},
            format="json", **auth_header(self.driver)
        )
        self.assertEqual(response.status_code, 403)

    def test_forged_token_is_rejected(self):
        response = self.set_status(self.driver.id, HTTP_AUTHORIZATION="Bearer forged.token.value")
        self.assertEqual(response.status_code, 401)

    def test_unapproved_drivers_old_token_stops_working(self):
        headers = auth_header(self.driver)
        Driver.objects.filter(id=self.driver.id).update(is_approved=False)
        self.assertEqual(self.set_status(self.driver.id, **headers).status_code, 401)

    def test_location_update_does_not_overwrite_status(self):
        # Updating the location from a stale object (status=OFFLINE) must keep BUSY in the database
        stale = Driver.objects.get(id=self.driver.id)
        Driver.objects.filter(id=self.driver.id).update(status="BUSY")
        stale.update_location(41.3, 69.2)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, "BUSY")
