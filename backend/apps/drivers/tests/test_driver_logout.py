from django.conf import settings
from django.core import signing
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.functions import create_driver_token
from apps.drivers.functions.create_driver_token import TOKEN_SALT

from .constants import LOCMEM_CACHE
from .functions import auth_header, make_driver


@override_settings(CACHES=LOCMEM_CACHE)
class DriverLogoutTests(TestCase):
    """A token can be revoked: logout ends every session of the driver."""

    def setUp(self):
        self.api = APIClient()
        self.driver = make_driver()

    def wallet(self, headers):
        return self.api.get("/api/wallet/info/", **headers)

    def test_logout_revokes_all_tokens(self):
        bot, panel = auth_header(self.driver), auth_header(self.driver)
        self.assertEqual(self.api.post("/api/drivers/logout/", **panel).status_code, 200)
        self.assertEqual(self.wallet(bot).status_code, 401)
        self.assertEqual(self.wallet(panel).status_code, 401)

    def test_new_login_works_after_logout(self):
        self.api.post("/api/drivers/logout/", **auth_header(self.driver))
        self.driver.refresh_from_db()
        self.assertEqual(self.wallet(auth_header(self.driver)).status_code, 200)

    def test_token_without_version_is_rejected(self):
        # Tokens issued before token_version existed
        old = signing.dumps({"driver_id": self.driver.id}, key=settings.DRIVER_TOKEN_SECRET_KEY, salt=TOKEN_SALT)
        self.assertEqual(self.wallet({"HTTP_AUTHORIZATION": f"Bearer {old}"}).status_code, 401)

    def test_rotating_token_key_logs_everyone_out(self):
        headers = auth_header(self.driver)
        with self.settings(DRIVER_TOKEN_SECRET_KEY="rotated-key"):
            self.assertEqual(self.wallet(headers).status_code, 401)

    def test_token_still_valid_without_logout(self):
        token = create_driver_token(self.driver)
        self.assertEqual(self.wallet({"HTTP_AUTHORIZATION": f"Bearer {token}"}).status_code, 200)
