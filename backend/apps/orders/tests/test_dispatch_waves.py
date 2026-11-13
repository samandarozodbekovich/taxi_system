from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.dispatch.models import OrderDispatch
from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.functions import reject_by_driver
from apps.orders.tasks import dispatch_new_order

from .functions import make_client, make_dispatch, make_order


@override_settings(CACHES=LOCMEM_CACHE)
@patch("apps.drivers.functions.notify_drivers_new_order")
class DispatchWaveTests(TestCase):
    """If the first drivers don't take the order, the next wave offers it to others."""

    def setUp(self):
        self.order = make_order(make_client(8001))
        # No locations - every wave falls back to all online drivers not offered yet
        self.first = make_driver("DRV-AAAAA1", status="ONLINE", telegram_id=111)

    def offered_driver_ids(self):
        return set(OrderDispatch.objects.filter(order=self.order).values_list("driver_id", flat=True))

    def test_no_new_wave_while_offers_are_open(self, notify):
        dispatch_new_order(self.order.id)
        make_driver("DRV-BBBBB2", status="ONLINE", telegram_id=222)
        dispatch_new_order(self.order.id)

        self.assertEqual(self.offered_driver_ids(), {self.first.id})
        self.order.refresh_from_db()
        self.assertEqual(self.order.dispatch_wave, 1)

    def test_next_wave_after_offers_expire(self, notify):
        dispatch_new_order(self.order.id)
        OrderDispatch.objects.filter(order=self.order).update(expires_at=self.order.created_at)
        second = make_driver("DRV-BBBBB2", status="ONLINE", telegram_id=222)
        dispatch_new_order(self.order.id)

        self.assertEqual(self.offered_driver_ids(), {self.first.id, second.id})
        self.order.refresh_from_db()
        self.assertEqual(self.order.dispatch_wave, 2)

    def test_last_rejection_starts_next_wave(self, notify):
        make_dispatch(self.order, self.first)
        with self.captureOnCommitCallbacks() as callbacks:
            reject_by_driver(self.order.id, self.first)
        self.assertEqual(len(callbacks), 1)

    def test_rejection_waits_for_others_in_the_wave(self, notify):
        make_dispatch(self.order, self.first)
        make_dispatch(self.order, make_driver("DRV-BBBBB2", status="ONLINE", telegram_id=222))
        with self.captureOnCommitCallbacks() as callbacks:
            reject_by_driver(self.order.id, self.first)
        self.assertEqual(len(callbacks), 0)
