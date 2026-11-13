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

    def test_panel_login_sets_httponly_cookie_not_token(self):
        make_driver()
        response = self.login("DRV-TEST01", "secret123")
        self.assertEqual(response.status_code, 200)
        # The token never reaches JavaScript
        self.assertNotIn("token", response.data)
        cookie = response.cookies["driver_token"]
        self.assertTrue(cookie.value)
        self.assertTrue(cookie["httponly"])

    @override_settings(BOT_API_SECRET="test-bot-secret")
    def test_bot_login_returns_token(self):
        make_driver()
        response = self.api.post(
            "/api/drivers/login/", {"driver_code": "DRV-TEST01", "password": "secret123"},
            format="json", HTTP_X_BOT_SECRET="test-bot-secret", HTTP_X_TELEGRAM_ID="111",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertNotIn("driver_token", response.cookies)

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

    def test_lockout_from_one_ip_does_not_block_other_ips(self):
        make_driver()
        for _ in range(5):
            self.login("DRV-TEST01", "wrong-pass")
        response = self.api.post(
            "/api/drivers/login/", {"driver_code": "DRV-TEST01", "password": "secret123"},
            format="json", REMOTE_ADDR="10.0.0.2"
        )
        self.assertEqual(response.status_code, 200)

    @override_settings(BOT_API_SECRET="test-bot-secret")
    def test_bot_lockout_is_per_telegram_user(self):
        make_driver()

        def bot_login(telegram_id, password):
            return self.api.post(
                "/api/drivers/login/", {"driver_code": "DRV-TEST01", "password": password}, format="json",
                HTTP_X_BOT_SECRET="test-bot-secret", HTTP_X_TELEGRAM_ID=str(telegram_id)
            )

        for _ in range(5):
            bot_login(111, "wrong-pass")
        self.assertEqual(bot_login(111, "secret123").status_code, 429)
        # The real driver logs in through the same bot (same IP) from their own Telegram account
        self.assertEqual(bot_login(222, "secret123").status_code, 200)

    def test_telegram_id_header_without_bot_secret_is_ignored(self):
        make_driver()
        for telegram_id in range(5):
            self.api.post(
                "/api/drivers/login/", {"driver_code": "DRV-TEST01", "password": "wrong-pass"},
                format="json", HTTP_X_TELEGRAM_ID=str(telegram_id)
            )
        # All counted against the IP, so a forged header can't buy more guesses
        self.assertEqual(self.login("DRV-TEST01", "secret123").status_code, 429)
