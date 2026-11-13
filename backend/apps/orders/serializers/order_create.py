from rest_framework import serializers

from ..models import Order
from ..functions import create_order

# Longer text is not an address (and would bloat Telegram messages to drivers)
MAX_ADDRESS_LENGTH = 300

class OrderCreateSerializer(serializers.ModelSerializer):
    # Field names match the names the bot sends
    pickup_latitude = serializers.FloatField(write_only=True)
    pickup_longitude = serializers.FloatField(write_only=True)
    destination_latitude = serializers.FloatField(write_only=True, required=False, default=0)
    destination_longitude = serializers.FloatField(write_only=True, required=False, default=0)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'pickup_latitude', 'pickup_longitude', 'pickup_address',
            'destination_latitude', 'destination_longitude',
            'destination_address', 'estimated_price', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'estimated_price', 'status', 'created_at']

    def validate(self, attrs):
        # Validate coordinates
        p_lat = attrs.get('pickup_latitude')
        p_lon = attrs.get('pickup_longitude')
        if not (-90 <= p_lat <= 90) or not (-180 <= p_lon <= 180):
            raise serializers.ValidationError("Invalid coordinates.")

        # Validate the address. Characters like # & % are allowed - real addresses use them
        # ("Building 4, apt #12"); addresses are escaped where they are shown instead
        # (html.escape in Telegram messages, innerText in the Mini Apps, the admin escapes too)
        address = attrs.get('pickup_address', '')
        if not address.strip():
            raise serializers.ValidationError("Pickup address must not be empty.")
        for field in ('pickup_address', 'destination_address'):
            if len(attrs.get(field) or '') > MAX_ADDRESS_LENGTH:
                raise serializers.ValidationError(f"The address is too long (max {MAX_ADDRESS_LENGTH} characters).")

        return attrs

    def create(self, validated_data):
        # The view resolves the client from authentication (the request body is not trusted)
        client = self.context['client']

        if client.is_currently_blocked:
            raise serializers.ValidationError("Your account is blocked.")

        return create_order(
            client=client,
            pickup_lat=validated_data.pop('pickup_latitude'),
            pickup_lon=validated_data.pop('pickup_longitude'),
            destination_lat=validated_data.pop('destination_latitude'),
            destination_lon=validated_data.pop('destination_longitude'),
            pickup_address=validated_data.pop('pickup_address'),
            destination_address=validated_data.pop('destination_address', '')
        )
