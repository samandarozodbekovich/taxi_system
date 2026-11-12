from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.clients.tests.functions import TEST_BOT_TOKEN, make_init_data
from apps.drivers.tests.constants import LOCMEM_CACHE

from .functions import make_client, make_order


@override_settings(CACHES=LOCMEM_CACHE, CLIENT_BOT_TOKEN=TEST_BOT_TOKEN, BOT_API_SECRET="test-bot-secret")
class ClientOrderAuthTests(TestCase):

    def setUp(self):
        self.api = APIClient()
        self.alice = make_client(2001)
        self.bob = make_client(2002)

    def tma(self, telegram_id):
        return {"HTTP_AUTHORIZATION": f"tma {make_init_data(telegram_id)}"}

    def test_active_order_without_init_data_is_401(self):
        self.assertEqual(self.api.get("/api/orders/active/").status_code, 401)

    def test_forged_init_data_is_rejected(self):
        forged = make_init_data(2001, bot_token="999:OTHER")
        self.assertEqual(self.api.get("/api/orders/active/", HTTP_AUTHORIZATION=f"tma {forged}").status_code, 401)

    def test_client_cannot_cancel_someone_elses_order(self):
        order = make_order(self.alice)
        response = self.api.post(f"/api/orders/{order.id}/cancel/", {}, format="json", **self.tma(2002))
        self.assertEqual(response.status_code, 400)
        order.refresh_from_db()
        self.assertEqual(order.status, "SEARCHING")

    def test_client_can_cancel_own_order(self):
        order = make_order(self.alice)
        response = self.api.post(f"/api/orders/{order.id}/cancel/", {}, format="json", **self.tma(2001))
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "CANCELED")

    def test_active_order_is_resolved_from_init_data(self):
        order = make_order(self.alice)
        self.assertEqual(self.api.get("/api/orders/active/", **self.tma(2001)).data["id"], order.id)
        self.assertFalse(self.api.get("/api/orders/active/", **self.tma(2002)).data["active"])

    def test_client_check_requires_bot_secret(self):
        self.assertEqual(self.api.get("/api/clients/check/2001/").status_code, 403)
        response = self.api.get("/api/clients/check/2001/", HTTP_X_BOT_SECRET="test-bot-secret")
        self.assertEqual(response.status_code, 200)
