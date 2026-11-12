from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.clients.models import Client
from apps.clients.permissions import IsClientBot
from apps.clients.serializers import ClientSerializer


class ClientCheckView(APIView):
    # Only the client bot (X-Bot-Secret) may call this - otherwise phone numbers could be harvested by tg_id
    authentication_classes = []
    permission_classes = [IsClientBot]

    def get(self, request, tg_id):
        client = Client.objects.filter(telegram_id=tg_id).first()
        if client is None:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClientSerializer(client).data)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
