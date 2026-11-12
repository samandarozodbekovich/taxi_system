from rest_framework import permissions

from apps.clients.models import Client


class IsClient(permissions.BasePermission):
    message = "Please open the app from Telegram."

    def has_permission(self, request, view):
        return isinstance(request.user, Client)
