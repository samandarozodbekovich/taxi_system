from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models import Order
from ..serializers import OrderCreateSerializer
from apps.clients.mixins import ClientAuthMixin

class OrderCreateView(ClientAuthMixin, APIView):

    def post(self, request):
        # The client is resolved from signed initData (or the bot secret), not from client_telegram_id in the body
        client = request.user

        active_order_error = Response(
            {"error": "You already have an active order. Please complete or cancel it before creating a new one."},
            status=status.HTTP_400_BAD_REQUEST
        )

        # Fast path for a clear message. The race (2 concurrent requests) is caught by the database's
        # one_active_order_per_client constraint - see the IntegrityError below
        if Order.objects.filter(client=client, status__in=Order.ACTIVE_STATUSES).exists():
            return active_order_error
        
        serializer = OrderCreateSerializer(data=request.data, context={'request': request, 'client': client})
        if serializer.is_valid():
            try:
                order = serializer.save()
            except IntegrityError:
                return active_order_error
            # Drivers are notified in Celery (schedule_dispatch) - not awaited here
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
