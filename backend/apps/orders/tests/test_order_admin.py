from types import SimpleNamespace

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.admin import OrderAdmin
from apps.orders.forms import OrderAdminForm
from apps.orders.models import Order
from apps.wallet.models import WalletTransaction

from .functions import make_client, make_order


@override_settings(CACHES=LOCMEM_CACHE)
class OrderAdminStatusTests(TestCase):
    """A status changed in the admin has the same side effects as in the apps."""

    def setUp(self):
        self.driver = make_driver("DRV-AAAAA1", status="BUSY")
        self.order = make_order(make_client(9001), "IN_PROGRESS", self.driver)
        self.admin = OrderAdmin(Order, AdminSite())

    def save_with_status(self, status):
        self.order.status = status
        form = SimpleNamespace(changed_data=["status"], initial={"status": "IN_PROGRESS"})
        self.admin.save_model(request=None, obj=self.order, form=form, change=True)
        self.order.refresh_from_db()
        self.driver.refresh_from_db()

    def test_complete_charges_commission_and_frees_driver(self):
        self.save_with_status("COMPLETED")
        self.assertEqual(self.order.status, "COMPLETED")
        self.assertEqual(self.driver.status, "ONLINE")
        self.assertTrue(WalletTransaction.objects.filter(order=self.order, transaction_type="COMMISSION").exists())

    def test_cancel_frees_driver(self):
        self.save_with_status("CANCELED")
        self.assertEqual(self.order.status, "CANCELED")
        self.assertEqual(self.order.cancel_by, "OPERATOR")
        self.assertEqual(self.driver.status, "ONLINE")

    def test_form_refuses_statuses_set_by_the_driver(self):
        order = make_order(make_client(9002), "ACCEPTED", self.driver)
        form = OrderAdminForm(instance=order)
        form.cleaned_data = {"status": "WAITING"}
        with self.assertRaises(ValidationError):
            form.clean_status()
