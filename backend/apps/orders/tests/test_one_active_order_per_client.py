from django.db import IntegrityError, transaction
from django.test import TestCase

from .functions import make_client, make_order


class OneActiveOrderPerClientTests(TestCase):

    def test_second_active_order_is_rejected_by_database(self):
        client = make_client(3001)
        make_order(client, "SEARCHING")
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_order(client, "ACCEPTED")

    def test_finished_orders_do_not_count(self):
        client = make_client(3002)
        make_order(client, "COMPLETED")
        make_order(client, "CANCELED")
        make_order(client, "SEARCHING")  # must not raise
