"""
Django settings for money_moe project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os, json
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

with open("/etc/config.json") as config_file:
    config = json.load(config_file)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = str(config.get("DEBUG")) == "1"

ALLOWED_HOSTS = ['www.zarathustrust.com', 'zarathustrust.com', '165.227.37.14', '127.0.0.1', 'localhost']

INTERNAL_IPS = (
    '127.0.0.1'
)

# models primary key
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Application definition

INSTALLED_APPS = [
    "users.apps.UsersConfig",
    "accounts.apps.AccountsConfig",
    "api.apps.ApiConfig",
    
    "crispy_forms",
    "rosetta",
    # "axes",
    "mathfilters",
    "django_countries",
    "crispy_bootstrap5",
    "django_htmx",
    "captcha",
    "admin_interface",
    "colorfield",
    "corsheaders",
    "rest_framework",

    'rest_framework_simplejwt.token_blacklist',

    "django.contrib.postgres",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "crum.CurrentRequestUserMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "axes.middleware.AxesMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "corsheaders.middleware.CorsPostCsrfMiddleware",
]

AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    # "axes.backends.AxesBackend",
    # Django ModelBackend is the default authentication backend.
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "money_moe.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, 'frontend/build')
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "money_moe.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

if DEBUG:
    # SQLITE3
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    # POSTGRESQL
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": config.get("db_name"),
            "USER": config.get("db_user"),
            "PASSWORD": config.get("db_pass"),
            "HOST": config.get("db_host"),
            "PORT": "5432",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "users.CustomUser"

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Toronto"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# USE_THOUSAND_SEPARATOR = True

LANGUAGES = [("de", _("German")), ("en", _("English"))]
LANGUAGE_COOKIE_NAME = "cookie_monster_lang"
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = True


LOCALE_PATHS = [os.path.join(BASE_DIR, "locale/")]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "static")  #'/home/moe/money_moe/static/'
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'frontend/build/static')
]


# Crispy Forms
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"


# CELERY
CELERY_BROKER_URL = config.get("BROKER_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BAKCEND = "amqp://"
CELERY_TIMEZONE = "EST"
CELERY_TASK_TRACK_STARTED = True
CELERYD_PREFETCH_MULTIPLIER = 1
# CELERY_TASK_TIME_LIMIT = 30 * 60


# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config.get("EMAIL_ID")
EMAIL_HOST_PASSWORD = config.get("EMAIL_PW")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# EMAIL_USE_SSL = False


# LOGIN
LOGIN_URL = "/login/"
# LOGIN_REDIRECT_URL = "/"


# AXES LOGIN
# AXES_FAILURE_LIMIT = 3
# AXES_COOLOFF_TIME = timedelta(minutes=3)
# AXES_LOCKOUT_TEMPLATE = "users/login_timeout.html"


# STRIPE
STRIPE_PUBLIC_KEY = config.get("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = config.get("STRIPE_SECRET_KEY")


# CORS & Django REST FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
    'http://localhost:8000',
    'https://www.zarathustrust.com'
)

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'https://www.zarathustrust.com'
]

CORS_ALLOWED_ORIGIN_REGEXES = [
r"^https://\w+\.zarathustrust\.com$",
]

CORS_ALLOW_CREDENTIALS = True

# SIMPLE JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}


# HTTPS settings
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 2592000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = "DENY"

