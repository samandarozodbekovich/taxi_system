from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import auth_header, make_driver
from apps.wallet.models import DriverWallet, WalletTransaction

from .functions import make_client, make_order


@override_settings(CACHES=LOCMEM_CACHE)
class DriverOrderActionTests(TestCase):

    def setUp(self):
        self.api = APIClient()
        self.client_obj = make_client(1001)
        self.driver = make_driver("DRV-AAAAA1", status="BUSY")
        self.other = make_driver("DRV-BBBBB2", status="ONLINE")

    def action(self, order, action, driver):
        return self.api.post(f"/api/orders/{order.id}/action/", {"action": action}, format="json", **auth_header(driver))

    def assert_status(self, order, status):
        order.refresh_from_db()
        self.assertEqual(order.status, status)

    def test_action_without_token_is_401(self):
        order = make_order(self.client_obj, "ACCEPTED", self.driver)
        response = self.api.post(f"/api/orders/{order.id}/action/", {"action": "arrive"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_unknown_action_is_400(self):
        order = make_order(self.client_obj, "ACCEPTED", self.driver)
        self.assertEqual(self.action(order, "fly", self.driver).status_code, 400)

    def test_other_driver_cannot_change_status(self):
        order = make_order(self.client_obj, "ACCEPTED", self.driver)
        self.assertEqual(self.action(order, "arrive", self.other).status_code, 400)
        self.assert_status(order, "ACCEPTED")

    def test_cannot_start_searching_order(self):
        order = make_order(self.client_obj, "SEARCHING")
        self.assertEqual(self.action(order, "start", self.driver).status_code, 400)
        self.assert_status(order, "SEARCHING")

    def test_owner_follows_status_sequence(self):
        order = make_order(self.client_obj, "ACCEPTED", self.driver)
        self.assertEqual(self.action(order, "arrive", self.driver).status_code, 200)
        self.assertEqual(self.action(order, "start", self.driver).status_code, 200)
        self.assert_status(order, "IN_PROGRESS")

    def test_other_driver_cannot_complete(self):
        order = make_order(self.client_obj, "IN_PROGRESS", self.driver)
        self.assertEqual(self.action(order, "complete", self.other).status_code, 400)
        self.assert_status(order, "IN_PROGRESS")

    def test_complete_charges_commission_atomically(self):
        order = make_order(self.client_obj, "IN_PROGRESS", self.driver)
        self.assertEqual(self.action(order, "complete", self.driver).status_code, 200)
        self.assert_status(order, "COMPLETED")
        self.driver.refresh_from_db()
        self.assertEqual(self.driver.status, "ONLINE")
        # Commission is charged from the single balance (DriverWallet) and logged
        wallet = DriverWallet.objects.get(driver=self.driver)
        self.assertEqual(wallet.balance, -order.commission_amount)
        transaction = WalletTransaction.objects.get(wallet=wallet, order=order)
        self.assertEqual(transaction.transaction_type, "COMMISSION")
        self.assertEqual(transaction.after_balance, wallet.balance)
