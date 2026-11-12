from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.clients.models import Client
from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import auth_header, make_driver
from apps.orders.tests.functions import make_client, make_order
from apps.referrals.models import ReferralBonus

BOT = {"HTTP_X_BOT_SECRET": "test-bot-secret"}


@override_settings(CACHES=LOCMEM_CACHE, BOT_API_SECRET="test-bot-secret")
class ReferralBonusTests(TestCase):

    def setUp(self):
        self.api = APIClient()
        self.inviter = make_client(7001)
        self.driver = make_driver("DRV-AAAAA1", status="BUSY")

    def register(self, telegram_id, code):
        return self.api.post("/api/clients/register/", {
            "telegram_id": telegram_id, "full_name": "Friend", "phone_number": "+998900000000",
            "invited_by_code": code,
        }, format="json", **BOT)

    def complete_trip(self, client):
        order = make_order(client, "IN_PROGRESS", self.driver)
        response = self.api.post(f"/api/orders/{order.id}/action/", {"action": "complete"}, format="json",
                                 **auth_header(self.driver))
        self.assertEqual(response.status_code, 200)

    def test_registration_with_code_links_the_inviter(self):
        self.assertEqual(self.register(7002, self.inviter.referral_code.lower()).status_code, 201)
        self.assertEqual(Client.objects.get(telegram_id=7002).referred_by, self.inviter)

    def test_unknown_code_is_ignored(self):
        self.assertEqual(self.register(7003, "NOPE").status_code, 201)
        self.assertIsNone(Client.objects.get(telegram_id=7003).referred_by)

    def test_bonus_is_paid_once_after_first_trip(self):
        self.register(7004, self.inviter.referral_code)
        friend = Client.objects.get(telegram_id=7004)

        self.complete_trip(friend)
        self.complete_trip(friend)

        self.inviter.refresh_from_db()
        self.assertEqual(self.inviter.bonus_balance, Decimal("5000"))
        self.assertEqual(ReferralBonus.objects.filter(referred=friend).count(), 1)

    def test_bonus_endpoint(self):
        self.register(7005, self.inviter.referral_code)
        response = self.api.get("/api/clients/bonus/", {"client_telegram_id": 7001}, **BOT)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["referral_code"], self.inviter.referral_code)
        self.assertEqual(response.data["invited_count"], 1)
