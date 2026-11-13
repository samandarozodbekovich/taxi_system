from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.functions import DRIVER_TOKEN_COOKIE, create_driver_token

from .constants import LOCMEM_CACHE
from .functions import make_driver

PANEL_HEADER = {"HTTP_X_REQUESTED_WITH": "driver-panel"}


@override_settings(CACHES=LOCMEM_CACHE)
class DriverCookieAuthTests(TestCase):
    """The panel authenticates with the HttpOnly cookie; changes also need the panel header (CSRF)."""

    def setUp(self):
        self.api = APIClient()
        self.driver = make_driver()
        self.api.cookies[DRIVER_TOKEN_COOKIE] = create_driver_token(self.driver)

    def set_status(self, **headers):
        return self.api.post(f"/api/drivers/{self.driver.id}/status/", {"is_online": True}, format="json", **headers)

    def test_read_with_cookie(self):
        response = self.api.get("/api/drivers/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.driver.id)

    def test_change_with_cookie_and_panel_header(self):
        self.assertEqual(self.set_status(**PANEL_HEADER).status_code, 200)

    def test_change_with_cookie_alone_is_refused(self):
        # What a forged form or fetch from another site would send: the cookie, but no custom header
        self.assertEqual(self.set_status().status_code, 403)
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, "OFFLINE")

    def test_logout_clears_cookie_and_revokes_token(self):
        old_token = self.api.cookies[DRIVER_TOKEN_COOKIE].value
        response = self.api.post("/api/drivers/logout/", **PANEL_HEADER)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.cookies[DRIVER_TOKEN_COOKIE].value, "")

        # Even a copy of the old cookie no longer works
        self.api.cookies[DRIVER_TOKEN_COOKIE] = old_token
        self.assertEqual(self.api.get("/api/drivers/me/").status_code, 401)
