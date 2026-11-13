from django.test import SimpleTestCase

from apps.orders.serializers.order_create import OrderCreateSerializer

VALID = {"pickup_latitude": 41.3, "pickup_longitude": 69.2, "pickup_address": "Point A"}


class OrderCreateSerializerTests(SimpleTestCase):
    """Real addresses contain # & % - they are escaped where shown, not rejected."""

    def is_valid(self, **fields):
        return OrderCreateSerializer(data={**VALID, **fields}).is_valid()

    def test_address_with_special_characters_is_accepted(self):
        self.assertTrue(self.is_valid(pickup_address="Building 4, apt #12 & 50% off street"))

    def test_too_long_address_is_rejected(self):
        self.assertFalse(self.is_valid(destination_address="x" * 301))

    def test_empty_pickup_address_is_rejected(self):
        self.assertFalse(self.is_valid(pickup_address="   "))
