from rest_framework import serializers

from apps.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['telegram_id', 'full_name', 'username', 'phone_number', 'language_code']

    def create(self, validated_data):
        client, _ = Client.objects.get_or_create(
            telegram_id=validated_data.get('telegram_id'),
            defaults=validated_data
        )
        return client
