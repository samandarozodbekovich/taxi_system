from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.wallet.models import DriverWallet, WalletTransaction


@override_settings(CACHES=LOCMEM_CACHE)
class AdminPagesTests(TestCase):

    def setUp(self):
        self.client.force_login(User.objects.create_superuser("admin", "admin@example.com", "pass"))

    def test_admin_pages_open(self):
        for url in [
            "/api/admin/wallet/driverwallet/", "/api/admin/wallet/wallettransaction/",
            "/api/admin/wallet/wallettransaction/add/", "/api/admin/referrals/referralbonus/",
            "/api/admin/orders/order/", "/api/admin/drivers/driver/", "/api/admin/clients/client/",
        ]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_topup_added_in_admin_updates_balance(self):
        wallet = DriverWallet.objects.get(driver=make_driver())
        response = self.client.post("/api/admin/wallet/wallettransaction/add/", {
            "wallet": wallet.id, "transaction_type": "TOPUP", "amount": "25000", "note": "cash at the office",
        })
        self.assertEqual(response.status_code, 302)  # redirect = saved
        wallet.refresh_from_db()
        self.assertEqual(wallet.balance, Decimal("25000"))
        transaction = WalletTransaction.objects.get(wallet=wallet)
        self.assertEqual((transaction.before_balance, transaction.after_balance), (Decimal("0"), Decimal("25000")))
