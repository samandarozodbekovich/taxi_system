from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.models import Driver

from .constants import LOCMEM_CACHE

PAYLOAD = {
    "full_name": "New Driver",
    "phone_number": "+998901112233",
    "car_model": "Cobalt",
    "car_color": "White",
    "car_number": "01A123BC",
    "password": "secret123",
    "telegram_id": 555,
}


@override_settings(CACHES=LOCMEM_CACHE, BOT_API_SECRET="test-bot-secret")
class DriverRegisterTests(TestCase):
    """Only the driver bot may register drivers - otherwise anyone could claim someone's telegram_id."""

    def setUp(self):
        self.api = APIClient()

    def test_register_without_bot_secret_is_refused(self):
        response = self.api.post("/api/drivers/register/", PAYLOAD, format="json")
        self.assertIn(response.status_code, (401, 403))
        self.assertFalse(Driver.objects.exists())

    def test_bot_can_register(self):
        response = self.api.post("/api/drivers/register/", PAYLOAD, format="json", HTTP_X_BOT_SECRET="test-bot-secret")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Driver.objects.get().telegram_id, 555)
