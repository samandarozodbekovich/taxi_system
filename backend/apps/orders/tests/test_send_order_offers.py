from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.drivers.tests.constants import LOCMEM_CACHE
from apps.drivers.tests.functions import make_driver
from apps.orders.functions import send_order_offers_in_batches
from apps.orders.tasks import send_order_offers

from .functions import make_client, make_dispatch, make_order


@override_settings(CACHES=LOCMEM_CACHE)
@patch("apps.drivers.functions.notify_drivers_new_order")
class SendOrderOffersTests(TestCase):
    """A large broadcast is split into one-second batches instead of one long task."""

    def setUp(self):
        self.order = make_order(make_client(9301))

    def make_offered_drivers(self, count):
        drivers = [make_driver(f"DRV-{i:06d}", status="ONLINE", telegram_id=1000 + i) for i in range(count)]
        for driver in drivers:
            make_dispatch(self.order, driver)
        return [d.id for d in drivers]

    def test_first_batch_now_rest_scheduled_a_second_apart(self, notify):
        driver_ids = self.make_offered_drivers(60)
        with patch.object(send_order_offers, "apply_async") as schedule:
            send_order_offers_in_batches(self.order.id, driver_ids)

        self.assertEqual(len(notify.call_args.args[1]), 25)
        self.assertEqual([c.kwargs["countdown"] for c in schedule.call_args_list], [1, 2])
        self.assertEqual([len(c.kwargs["args"][1]) for c in schedule.call_args_list], [25, 10])

    def test_batch_is_skipped_once_the_order_is_taken(self, notify):
        driver_ids = self.make_offered_drivers(2)
        self.order.status = "ACCEPTED"
        self.order.save()
        send_order_offers(self.order.id, driver_ids)
        notify.assert_not_called()

    def test_rejected_offers_are_not_sent(self, notify):
        driver_ids = self.make_offered_drivers(2)
        self.order.dispatches.filter(driver_id=driver_ids[0]).update(is_rejected=True)
        send_order_offers(self.order.id, driver_ids)
        self.assertEqual([d.id for d in notify.call_args.args[1]], [driver_ids[1]])
