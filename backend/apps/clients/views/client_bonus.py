from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.mixins import ClientAuthMixin


class ClientBonusView(ClientAuthMixin, APIView):
    """Bonus balance and referral code of the client (Mini App initData or client bot)."""

    def get(self, request):
        client = request.user
        return Response({
            "bonus_balance": client.bonus_balance,
            "referral_code": client.referral_code,
            "invited_count": client.referrals.count(),
        })
