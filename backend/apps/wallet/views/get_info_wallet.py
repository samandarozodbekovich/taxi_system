from rest_framework.response import Response
from rest_framework.views import APIView

from apps.drivers.mixins import DriverAuthMixin
from apps.wallet.models import DriverWallet
from apps.wallet.serializers import GetInfoWalletSerializer


class InfoWalletView(DriverAuthMixin, APIView):

    def get(self, request):
        # The driver comes from the token; a missing wallet is created instead of returning 404
        wallet, _ = DriverWallet.objects.get_or_create(driver=request.user)
        return Response(GetInfoWalletSerializer(wallet).data)
