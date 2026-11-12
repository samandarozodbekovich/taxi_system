import time

from django.test import SimpleTestCase

from apps.clients.functions import verify_telegram_init_data

from .functions import TEST_BOT_TOKEN, make_init_data


class VerifyTelegramInitDataTests(SimpleTestCase):

    def test_valid_init_data_returns_user(self):
        self.assertEqual(verify_telegram_init_data(make_init_data(777), TEST_BOT_TOKEN)["id"], 777)

    def test_signed_with_other_bot_token_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_telegram_init_data(make_init_data(777, bot_token="999:OTHER"), TEST_BOT_TOKEN)

    def test_tampered_user_id_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_telegram_init_data(make_init_data(777).replace("777", "778"), TEST_BOT_TOKEN)

    def test_expired_init_data_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_telegram_init_data(make_init_data(777, auth_date=time.time() - 2 * 86400), TEST_BOT_TOKEN)

    def test_missing_hash_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_telegram_init_data("user=%7B%22id%22%3A1%7D&auth_date=1", TEST_BOT_TOKEN)

    def test_garbage_is_rejected(self):
        with self.assertRaises(ValueError):
            verify_telegram_init_data("%%%", TEST_BOT_TOKEN)
