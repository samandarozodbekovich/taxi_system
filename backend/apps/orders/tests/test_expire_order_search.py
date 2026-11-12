from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.drivers.tests.functions import make_driver
from apps.orders.models import Order
from apps.orders.tasks import expire_order_search

from .functions import make_client, make_order


class ExpireOrderSearchTests(TestCase):

    def setUp(self):
        self.client_obj = make_client(4001)

    def expire(self, order, started_minutes_ago=None):
        if started_minutes_ago is not None:
            started = timezone.now() - timedelta(minutes=started_minutes_ago)
            Order.objects.filter(id=order.id).update(searching_started_at=started)
        expire_order_search(order.id, 180)
        order.refresh_from_db()
        return order.status

    def test_timed_out_search_becomes_no_driver(self):
        self.assertEqual(self.expire(make_order(self.client_obj), started_minutes_ago=10), "NO_DRIVER")

    def test_restarted_search_is_not_expired_by_old_task(self):
        # searching_started_at is "now"
        self.assertEqual(self.expire(make_order(self.client_obj)), "SEARCHING")

    def test_accepted_order_is_not_touched(self):
        order = make_order(self.client_obj, "ACCEPTED", make_driver("DRV-CCCCC3"))
        self.assertEqual(self.expire(order, started_minutes_ago=10), "ACCEPTED")
