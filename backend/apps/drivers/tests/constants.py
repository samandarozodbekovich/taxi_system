# Tests must not require Redis (login lockout and throttling use the cache)
LOCMEM_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
