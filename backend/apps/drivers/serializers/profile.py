from rest_framework import serializers
from ..models import Driver


class DriverProfileSerializer(serializers.ModelSerializer):

    is_online = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = [
            'id',
            'driver_code',
            'full_name',
            'phone_number',
            'car_model',
            'car_color',
            'car_number',
            'photo',
            'status',
            'is_online',
            'wallet',
        ]

    def get_is_online(self, obj):
        
        return obj.status == 'ONLINE'