from rest_framework import permissions

from apps.drivers.models import Driver


class IsDriver(permissions.BasePermission):
    message = "Please log in as a driver."

    def has_permission(self, request, view):
        return isinstance(request.user, Driver)
