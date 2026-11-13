from django.test import SimpleTestCase

from apps.orders.functions import order_number_for
from apps.orders.models import Order


class OrderStatusMachineTests(SimpleTestCase):

    def test_allowed_transition(self):
        order = Order(status="ACCEPTED")
        order.transition_to("WAITING")
        self.assertEqual(order.status, "WAITING")

    def test_searching_cannot_jump_to_in_progress(self):
        order = Order(status="SEARCHING")
        with self.assertRaises(ValueError):
            order.transition_to("IN_PROGRESS")
        self.assertEqual(order.status, "SEARCHING")

    def test_final_statuses_are_terminal(self):
        for final in ("COMPLETED", "CANCELED"):
            for target in ("SEARCHING", "ACCEPTED", "IN_PROGRESS", "CANCELED"):
                self.assertFalse(Order(status=final).can_transition_to(target))

    def test_in_progress_cannot_go_back_to_searching(self):
        self.assertFalse(Order(status="IN_PROGRESS").can_transition_to("SEARCHING"))

    def test_order_number_from_id(self):
        self.assertEqual(order_number_for(42), "TX-000042")
