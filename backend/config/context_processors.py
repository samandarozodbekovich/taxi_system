from django.conf import settings


def frontend_keys(request):
    """Pass the (public) frontend keys to templates."""
    return {
        "YANDEX_FRONTEND_MAP_KEY": settings.YANDEX_FRONTEND_MAP_KEY or "",
    }
