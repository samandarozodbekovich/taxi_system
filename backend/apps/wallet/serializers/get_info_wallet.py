from rest_framework import serializers
from ..models import DriverWallet


class GetInfoWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverWallet
        fields = [
            "balance",
            "total_earned",
            "total_commission_paid",
            "total_penalty_paid",
            "updated_at"
        ]
        read_only_fields = fields