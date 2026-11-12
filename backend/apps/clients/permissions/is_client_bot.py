from rest_framework import permissions

from apps.clients.functions import bot_secret_is_valid


class IsClientBot(permissions.BasePermission):
    """Endpoints only the client bot may call (client lookup / registration)."""
    message = "Permission denied."

    def has_permission(self, request, view):
        return bot_secret_is_valid(request)
