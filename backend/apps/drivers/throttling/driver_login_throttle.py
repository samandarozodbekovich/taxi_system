from rest_framework.throttling import ScopedRateThrottle

from apps.drivers.functions import login_source


class DriverLoginThrottle(ScopedRateThrottle):
    """Login rate per source: per Telegram user for the driver bot, per IP for the panel."""

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": login_source(request)}
