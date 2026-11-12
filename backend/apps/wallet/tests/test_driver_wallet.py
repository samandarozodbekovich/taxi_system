from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import auth_header, make_driver
from apps.wallet.models import DriverWallet


@override_settings(CACHES=LOCMEM_CACHE)
class DriverWalletTests(TestCase):

    def test_new_driver_gets_a_wallet(self):
        driver = make_driver()
        self.assertTrue(DriverWallet.objects.filter(driver=driver).exists())

    def test_wallet_info_returns_balance(self):
        driver = make_driver()
        DriverWallet.objects.filter(driver=driver).update(balance=Decimal("50000"))
        response = APIClient().get("/api/wallet/info/", **auth_header(driver))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data["balance"]), Decimal("50000"))

    def test_wallet_info_creates_missing_wallet(self):
        driver = make_driver()
        DriverWallet.objects.filter(driver=driver).delete()
        response = APIClient().get("/api/wallet/info/", **auth_header(driver))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(response.data["balance"]), Decimal("0"))
