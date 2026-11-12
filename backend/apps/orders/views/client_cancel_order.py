from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.mixins import ClientAuthMixin
from apps.orders.functions import cancel_by_client


class OrderCancelByClientView(ClientAuthMixin, APIView):

    def post(self, request, order_id):
        # The client comes from initData - nobody can cancel someone else's order
        try:
            cancel_by_client(order_id, request.user, request.data.get('cancel_reason'))
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        return Response({"message": "Order canceled successfully."})
