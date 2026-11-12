from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.drivers.functions import new_order_message


class NewOrderMessageTests(SimpleTestCase):

    def test_client_address_is_html_escaped(self):
        order = SimpleNamespace(
            id=1, pickup_address='<a href="http://evil">Click</a>', destination_address="B",
            distance_km=3.0, estimated_price=20000,
        )
        text, _ = new_order_message(order)
        self.assertNotIn("<a href", text)
        self.assertIn("&lt;a href", text)
