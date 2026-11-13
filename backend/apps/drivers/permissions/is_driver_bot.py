from rest_framework import permissions

from apps.clients.functions import bot_secret_is_valid


class IsDriverBot(permissions.BasePermission):
    """Endpoints only the driver bot may call (registration - it vouches for the telegram_id)."""
    message = "Permission denied."

    def has_permission(self, request, view):
        return bot_secret_is_valid(request)
