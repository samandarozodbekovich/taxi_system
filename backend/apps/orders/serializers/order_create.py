from http import client
from urllib import request

from ...clients.models import Client
from rest_framework import serializers

from ..models import Order
from ..services import OrderService

class OrderCreateSerializer(serializers.ModelSerializer):
    # Field nomlarini bot yuborayotgan nomlarga moslaymiz
    pickup_latitude = serializers.FloatField(write_only=True)
    pickup_longitude = serializers.FloatField(write_only=True)
    destination_latitude = serializers.FloatField(write_only=True, required=False, default=0)
    destination_longitude = serializers.FloatField(write_only=True, required=False, default=0)
    client_telegram_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'pickup_latitude', 'pickup_longitude', 'pickup_address',
            'destination_latitude', 'destination_longitude', 'client_telegram_id',
            'destination_address', 'estimated_price', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'order_number', 'estimated_price', 'status', 'created_at']

    def validate(self, attrs):
        # Koordinatalarni tekshirish
        p_lat = attrs.get('pickup_latitude')
        p_lon = attrs.get('pickup_longitude')
        if not (-90 <= p_lat <= 90) or not (-180 <= p_lon <= 180):
            raise serializers.ValidationError("Koordinatalar noto'g'ri formatda.")

        # Manzilni tekshirish
        address = attrs.get('pickup_address', '')
        if not address.strip():
            raise serializers.ValidationError("Olib ketish manzili bo'sh bo'lmasligi kerak.")
        
        # Maxsus belgilarni tekshirish (to'g'rilangan variant)
        special_chars = ['#', '$', '%', '&', '*']
        if any(char in address for char in special_chars):
            raise serializers.ValidationError("Manzilda taqiqlangan belgilar bor.")
        
        return attrs

    def create(self, validated_data):
        tg_id = validated_data.pop('client_telegram_id')
        
        try:
            client = Client.objects.get(telegram_id=tg_id)
        except Client.DoesNotExist:
            raise serializers.ValidationError("Bunday Telegram ID ga ega mijoz topilmadi.")

        # OrderService orqali buyurtma yaratish
        # Eslatma: OrderService.create_order ichidagi argument nomlari 
        # modeldagi bilan bir xil ekanligiga ishonch hosil qiling
        order = OrderService.create_order(
            client=client,
            pickup_lat=validated_data.pop('pickup_latitude'),
            pickup_lon=validated_data.pop('pickup_longitude'),
            destination_lat=validated_data.pop('destination_latitude'),
            destination_lon=validated_data.pop('destination_longitude'),
            pickup_address=validated_data.pop('pickup_address'),
            destination_address=validated_data.pop('destination_address', '')
        )
        return order
