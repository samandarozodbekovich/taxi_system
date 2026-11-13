from rest_framework.throttling import BaseThrottle

from apps.clients.functions import bot_secret_is_valid


def login_source(request):
    """
    Who is trying to log in, for the login lockout and throttle. The driver bot sends every
    driver's login from one IP, so for its requests (X-Bot-Secret) the Telegram user it relays
    (X-Telegram-Id) is the source; otherwise (the panel) it is the client IP.
    """
    telegram_id = request.headers.get("X-Telegram-Id", "")
    if telegram_id.isdigit() and bot_secret_is_valid(request):
        return f"tg:{telegram_id}"
    # get_ident honours REST_FRAMEWORK['NUM_PROXIES'], so X-Forwarded-For can't be spoofed
    return f"ip:{BaseThrottle().get_ident(request)}"
