from django.core.cache import cache

LOCKOUT_SECONDS = 15 * 60


def record_failed_login(fail_key):
    """Count a failed attempt; the lockout window starts at the first one."""
    try:
        cache.incr(fail_key)
    except ValueError:
        cache.set(fail_key, 1, LOCKOUT_SECONDS)
