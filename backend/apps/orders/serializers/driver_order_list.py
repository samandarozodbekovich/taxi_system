from rest_framework import serializers
from apps.orders.models import Order


class DriverOrderListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name')
    pickup_lat = serializers.FloatField(source='pickup_location.y')
    pickup_lon = serializers.FloatField(source='pickup_location.x')

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'client_name', 'pickup_lat', 'pickup_lon', 
            'pickup_address', 'destination_address', 'estimated_price', 'distance_km'
        ]