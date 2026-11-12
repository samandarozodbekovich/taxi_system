from decimal import Decimal

from django.test import TestCase, override_settings

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.wallet.functions import apply_wallet_transaction
from apps.wallet.models import DriverWallet, WalletTransaction


@override_settings(CACHES=LOCMEM_CACHE)
class WalletTransactionTests(TestCase):

    def setUp(self):
        self.wallet = DriverWallet.objects.get(driver=make_driver())

    def apply(self, transaction_type, amount):
        transaction = WalletTransaction(wallet=self.wallet, transaction_type=transaction_type, amount=Decimal(amount))
        apply_wallet_transaction(transaction)
        self.wallet.refresh_from_db()
        return transaction

    def test_topup_increases_balance_and_logs_before_after(self):
        transaction = self.apply("TOPUP", "50000")
        self.assertEqual(self.wallet.balance, Decimal("50000"))
        self.assertEqual((transaction.before_balance, transaction.after_balance), (Decimal("0"), Decimal("50000")))

    def test_penalty_decreases_balance_and_counts_penalties(self):
        self.apply("TOPUP", "50000")
        self.apply("PENALTY", "2000")
        self.assertEqual(self.wallet.balance, Decimal("48000"))
        self.assertEqual(self.wallet.total_penalty_paid, Decimal("2000"))

    def test_commission_cannot_be_added_manually(self):
        with self.assertRaises(ValueError):
            self.apply("COMMISSION", "1000")

    def test_amount_must_be_positive(self):
        with self.assertRaises(ValueError):
            self.apply("TOPUP", "-5")
