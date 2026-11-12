from rest_framework import serializers

from ..models import Order


class OrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'pickup_address', 'destination_address',
            'distance_km', 'total_price', 'created_at', 'completed_at',
        ]
