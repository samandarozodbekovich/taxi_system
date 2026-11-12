from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .constants import LOCMEM_CACHE
from .functions import make_driver


@override_settings(CACHES=LOCMEM_CACHE)
class DriverLoginTests(TestCase):

    def setUp(self):
        # Lockout counters and throttle history live in the cache - start every test clean
        cache.clear()
        self.api = APIClient()

    def login(self, code, password):
        return self.api.post("/api/drivers/login/", {"driver_code": code, "password": password}, format="json")

    def test_login_returns_token(self):
        make_driver()
        response = self.login("DRV-TEST01", "secret123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_unknown_code_and_wrong_password_give_same_message(self):
        make_driver()
        unknown = self.login("DRV-NOPE00", "secret123")
        wrong = self.login("DRV-TEST01", "wrong-pass")
        self.assertEqual(unknown.status_code, 400)
        self.assertEqual(unknown.data, wrong.data)

    def test_unapproved_driver_cannot_login(self):
        make_driver(approved=False)
        response = self.login("DRV-TEST01", "secret123")
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("token", response.data)

    def test_lockout_after_too_many_failed_attempts(self):
        make_driver()
        for _ in range(5):
            self.assertEqual(self.login("DRV-TEST01", "wrong-pass").status_code, 400)
        # Even the correct password is refused while the lockout lasts
        self.assertEqual(self.login("DRV-TEST01", "secret123").status_code, 429)
