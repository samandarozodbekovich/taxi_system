from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import auth_header, make_driver
from apps.wallet.models import DriverWallet

from .functions import make_client, make_dispatch, make_order


@override_settings(CACHES=LOCMEM_CACHE)
class AcceptOrderTests(TestCase):
    """A driver may accept or view only an order that was offered to them."""

    def setUp(self):
        self.api = APIClient()
        self.driver = make_driver("DRV-AAAAA1", status="ONLINE")
        self.order = make_order(make_client(5001))

    def accept(self):
        return self.api.post(
            f"/api/orders/{self.order.id}/action/", {"action": "accept"}, format="json", **auth_header(self.driver)
        )

    def detail(self):
        return self.api.get(f"/api/orders/{self.order.id}/detail/", **auth_header(self.driver))

    def assert_status(self, status):
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, status)

    def test_cannot_accept_order_not_offered(self):
        self.assertEqual(self.accept().status_code, 400)
        self.assert_status("SEARCHING")

    def test_can_accept_offered_order(self):
        make_dispatch(self.order, self.driver)
        self.assertEqual(self.accept().status_code, 200)
        self.assert_status("ACCEPTED")

    def test_cannot_accept_expired_offer(self):
        make_dispatch(self.order, self.driver, expires_in_seconds=-1)
        self.assertEqual(self.accept().status_code, 400)
        self.assert_status("SEARCHING")

    def test_cannot_accept_rejected_offer(self):
        make_dispatch(self.order, self.driver, is_rejected=True)
        self.assertEqual(self.accept().status_code, 400)
        self.assert_status("SEARCHING")

    def test_cannot_accept_with_negative_balance(self):
        make_dispatch(self.order, self.driver)
        DriverWallet.objects.filter(driver=self.driver).update(balance=-1000)
        self.assertEqual(self.accept().status_code, 400)
        self.assert_status("SEARCHING")

    def test_new_driver_with_zero_balance_can_accept(self):
        make_dispatch(self.order, self.driver)
        self.assertTrue(DriverWallet.objects.get(driver=self.driver).can_accept_order())
        self.assertEqual(self.accept().status_code, 200)

    def test_cannot_view_details_of_order_not_offered(self):
        self.assertEqual(self.detail().status_code, 403)

    def test_can_view_details_of_offered_order(self):
        make_dispatch(self.order, self.driver)
        self.assertEqual(self.detail().status_code, 200)
