import hmac

from django.conf import settings


def bot_secret_is_valid(request):
    """True if the request carries the client bot's X-Bot-Secret header."""
    expected = settings.BOT_API_SECRET
    received = request.headers.get("X-Bot-Secret", "")
    return bool(expected) and hmac.compare_digest(received.encode(), expected.encode())
