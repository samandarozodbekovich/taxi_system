from dotenv import load_dotenv
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Always read .env from backend/, regardless of the working directory
load_dotenv(BASE_DIR / '.env')


def env_list(name, default=""):
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


def env_required(name):
    value = os.getenv(name)
    if not value:
        raise ImproperlyConfigured(f"{name} is not set in .env.")
    return value


# Secrets come only from .env - no defaults in code.
# (The previously hard-coded SECRET_KEY is still in git history; don't use it.)
SECRET_KEY = env_required("DJANGO_SECRET_KEY")

# Defaults to production mode. For local development set DJANGO_DEBUG=True in .env.
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("1", "true", "yes")

# Not "*" - only allowed domains (e.g. localhost,127.0.0.1,example.ngrok-free.dev)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")

CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# HTTPS is terminated by the proxy in front (nginx / ngrok). No SSL redirect or HSTS here:
# the bots call the backend over plain http://backend:8000 inside Docker.
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
if int(os.getenv('DJANGO_NUM_PROXIES', '0')) > 0:
    # Trust the proxy's X-Forwarded-Proto so request.is_secure() is correct
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

YANDEX_FRONTEND_MAP_KEY=os.getenv('YANDEX_FRONTEND_MAP_KEY')

DRIVER_BOT_TOKEN=os.getenv("DRIVER_BOT_TOKEN")
DRIVER_WEBAPP_URL=os.getenv("DRIVER_WEBAPP_URL")

# Your own OSRM server (e.g. http://localhost:5000). If empty, the router.project-osrm.org demo server is used;
# it is for testing only: its usage policy forbids production use and it is rate-limited.
OSRM_BASE_URL = os.getenv("OSRM_BASE_URL", "")

# Mini App initData signatures are verified with this token (the client bot that opens the Mini App)
CLIENT_BOT_TOKEN = os.getenv("CLIENT_BOT_TOKEN")
# Shared secret for bot -> backend requests (X-Bot-Secret header), set in both bots' .env
BOT_API_SECRET = os.getenv("BOT_API_SECRET", "")
# Application definition

INSTALLED_APPS = [
    'daphne',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.gis',
    
    # installed packeges
    'rest_framework',
    'channels',
    
    # default django apps

    'apps.clients',
    'apps.drivers',
    'apps.orders',
    'apps.wallet',
    'apps.dispatch',
    'apps.referrals',
    'apps.settings_app',
    
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Serves static files (admin CSS/JS) when DEBUG=False, without nginx
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.frontend_keys",
            ],
        },
    },
]

# Use ASGI instead of WSGI
ASGI_APPLICATION = 'config.asgi.application'

# Redis server (Docker: "redis", local: 127.0.0.1). Databases: 0 Channels, 1 Celery, 2 cache, 3 driver bot FSM
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(REDIS_HOST, REDIS_PORT)],
            "expiry": 3600,
            "symmetric_encryption_keys": [SECRET_KEY], 
        },
    },
}

# WSGI_APPLICATION = "config.wsgi.application"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_THROTTLE_RATES': {
        # Driver login attempts per source: Telegram user for the driver bot, IP for the panel
        'driver_login': '30/min',
        # Route + price previews per client (each moved map pin is one request)
        'route': '60/min',
    },
    # Number of proxies in front of the server (ngrok/nginx - 1). Without it the IP came from a spoofable X-Forwarded-For.
    'NUM_PROXIES': int(os.getenv('DJANGO_NUM_PROXIES', '0')),
}

# Throttle and login lockout counters must be shared by all daphne/celery processes
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/2",
    }
}

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME', 'taxi_system_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': env_required('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

if os.name == 'nt':
    OSGEO4W = r"C:\OSGeo4W"
    os.environ['PATH'] = os.path.join(OSGEO4W, 'bin') + ';' + os.environ['PATH']
    GDAL_LIBRARY_PATH = r"C:\OSGeo4W\bin\gdal312.dll"
    GEOS_LIBRARY_PATH = r"C:\OSGeo4W\bin\geos_c.dll"


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
# collectstatic target, served by WhiteNoise
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Uploaded files (driver photos)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}


# ==============================================================================
# CELERY SETTINGS
# ==============================================================================

# Redis database 1 (so it doesn't interfere with Channels)
CELERY_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

# Stores task results (optional, but useful)
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Message format and timezone
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE  # same timezone as Django

# Retry logic if a task fails while running
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # A single task may run for at most 30 minutes

if not DEBUG and not OSRM_BASE_URL:
    import warnings
    warnings.warn("OSRM_BASE_URL is not set - the OSRM demo server is used in production (forbidden and rate-limited).")
