from dotenv import load_dotenv
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t6up2i&cnifme9-%546ar9me!urvzlo*caccs#l*p7h8i11#yf"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://repressed-jackpot-dolly.ngrok-free.dev',
]

YANDEX_ROUTING_API_KEY=os.getenv('YANDEX_ROUTING_API_KEY')
YANDEX_FRONTEND_MAP_KEY=os.getenv('YANDEX_FRONTEND_MAP_KEY')

DRIVER_BOT_TOKEN=os.getenv("DRIVER_BOT_TOKEN")
DRIVER_WEBAPP_URL=os.getenv("DRIVER_WEBAPP_URL")
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
            ],
        },
    },
]

# WSGI o'rniga ASGI ishlatamiz
ASGI_APPLICATION = 'config.asgi.application'

# Redis serveri (Docker yoki o'zida o'rnatilgan bo'lishi kerak)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "expiry": 3600,
            "symmetric_encryption_keys": [SECRET_KEY], 
        },
    },
}

# WSGI_APPLICATION = "config.wsgi.application"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'taxi_system_db',
        'USER': 'postgres',
        'PASSWORD': '12345',
        'HOST': 'localhost',  
        'PORT': '5432',      
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
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# ==============================================================================
# CELERY SETTINGS
# ==============================================================================

# Redis broker manzili (lokal server uchun standart port 6379)
CELERY_BROKER_URL = 'redis://localhost:6379/1'  # /1 - Redis ichidagi 1-baza (Channels-ga xalaqit bermasligi uchun)

# Vazifalar natijalarini saqlash uchun (ixtiyoriy, lekin kerak bo'ladi)
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

# Xabarlarni qabul qilish formati va vaqt zonasi
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE  # Djangodagi vaqt zonasi bilan birxil qiladi

# Agar vazifa bajarilayotganda xatolik yuz bersa, uni qayta urinish (retry) mantiqlari
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # Maksimal 30 daqiqa ishlashi mumkin bitta task