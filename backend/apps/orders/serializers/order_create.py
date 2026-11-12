from rest_framework import serializers

from ..models import Order
from ..functions import create_order

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

        # Validate the address
        address = attrs.get('pickup_address', '')
        if not address.strip():
            raise serializers.ValidationError("Pickup address must not be empty.")
        
        # Reject special characters
        special_chars = ['#', '$', '%', '&', '*']
        if any(char in address for char in special_chars):
            raise serializers.ValidationError("The address contains forbidden characters.")
        
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
