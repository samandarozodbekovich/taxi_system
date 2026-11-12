from rest_framework import serializers

from apps.clients.models import Client


class ClientSerializer(serializers.ModelSerializer):
    # Referral code of the inviter (from the bot link t.me/<bot>?start=<code>), optional
    invited_by_code = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Client
        fields = ['telegram_id', 'full_name', 'username', 'phone_number', 'language_code', 'invited_by_code']

    def create(self, validated_data):
        invited_by_code = validated_data.pop('invited_by_code', '').strip().upper()
        inviter = Client.objects.filter(referral_code=invited_by_code).first() if invited_by_code else None

        # get_or_create: an existing client is returned as is (the inviter can't be changed later)
        client, _ = Client.objects.get_or_create(
            telegram_id=validated_data.get('telegram_id'),
            defaults={**validated_data, 'referred_by': inviter},
        )
        return client
