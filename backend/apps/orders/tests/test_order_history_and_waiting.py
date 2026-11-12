from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import auth_header, make_driver
from apps.orders.models import Order

from .functions import make_client, make_order

BOT = {"HTTP_X_BOT_SECRET": "test-bot-secret"}


@override_settings(CACHES=LOCMEM_CACHE, BOT_API_SECRET="test-bot-secret")
class OrderHistoryTests(TestCase):

    def test_client_sees_only_own_orders(self):
        alice, bob = make_client(8001), make_client(8002)
        own = make_order(alice, "COMPLETED")
        make_order(bob, "COMPLETED")

        response = APIClient().get("/api/orders/history/", {"client_telegram_id": 8001}, **BOT)

        self.assertEqual(response.status_code, 200)
        self.assertEqual([o["id"] for o in response.data], [own.id])

    def test_history_requires_authentication(self):
        self.assertEqual(APIClient().get("/api/orders/history/").status_code, 401)


@override_settings(CACHES=LOCMEM_CACHE)
class WaitingPriceTests(TestCase):

    def start_trip_after_waiting(self, minutes):
        driver = make_driver("DRV-AAAAA1", status="BUSY")
        order = make_order(make_client(8101), "WAITING", driver)
        Order.objects.filter(id=order.id).update(arrived_at=timezone.now() - timedelta(minutes=minutes))
        response = APIClient().post(f"/api/orders/{order.id}/action/", {"action": "start"}, format="json",
                                    **auth_header(driver))
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        return order.waiting_price

    def test_waiting_beyond_free_time_is_charged(self):
        # 10 minutes - 3 free minutes = 7 paid minutes x 500 (defaults)
        self.assertEqual(self.start_trip_after_waiting(10), Decimal("3500"))

    def test_waiting_within_free_time_is_free(self):
        self.assertEqual(self.start_trip_after_waiting(2), Decimal("0"))
