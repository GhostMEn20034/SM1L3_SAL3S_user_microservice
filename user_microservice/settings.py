from datetime import timedelta
from pathlib import Path
import redis
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# If you want to use API Routes intended for microservices communication, you need to specify this key.
# WARNING: Store microservice key in .env file or server environment variables
MICROSERVICE_KEY = os.getenv("MICROSERVICE_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.getenv("DEBUG", default=0))

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")
AUTH_USER_MODEL = "accounts.Account"
AUTHENTICATION_BACKENDS = (
    # logging with username & password
    'django.contrib.auth.backends.ModelBackend',
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Own apps
    'apps.core',
    'apps.accounts',
    'apps.verification',
    'apps.addresses',
    'apps.products',
    'apps.carts',
    'apps.history',

    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'phonenumber_field',
    'django_countries',
    'corsheaders',
    'django_dramatiq',
    'dramatiq_crontab',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'user_microservice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'user_microservice.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DB_SSL_MODE = bool(int(os.getenv("DB_SSL_MODE", default=0)))

DATABASES = {
    'default': {
        "ENGINE": os.getenv("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("SQL_DATABASE", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.getenv("SQL_USER", "user"),
        "PASSWORD": os.getenv("SQL_PASSWORD", "password"),
        "HOST": os.getenv("SQL_HOST", "localhost"),
        "PORT": os.getenv("SQL_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("SQL_CONN_MAX_AGE", 0)),
        'OPTIONS': {
            'sslmode': 'require' if os.getenv("DB_SSL_MODE") == '1' else 'disable',
        },
    }
}

# Dramatiq Tasks
DRAMATIQ_BROKER_URL = os.getenv("DRAMATIQ_BROKER_URL", "redis://127.0.0.1:6379/0")
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "connection_pool": redis.ConnectionPool.from_url(DRAMATIQ_BROKER_URL)
    },
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        "dramatiq.middleware.TimeLimit",
        "dramatiq.middleware.Retries",
        "django_dramatiq.middleware.AdminMiddleware",
        "django_dramatiq.middleware.DbConnectionsMiddleware",
    ]
}

DRAMATIQ_CRONTAB = {
    "REDIS_URL": os.getenv("DRAMATIQ_CRONTAB_BROKER_URL", "redis://127.0.0.1:6379/0"),
}

DRAMATIQ_RESULT_BACKEND = {
    "BACKEND": "dramatiq.results.backends.redis.RedisBackend",
    "BACKEND_OPTIONS": {
        "url": os.getenv("DRAMATIQ_RESULT_BACKEND_URL", "redis://127.0.0.1:6379/1"),
    },
    "MIDDLEWARE_OPTIONS": {
        "result_ttl": 1000 * 60 * 10
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
if os.getenv("STATIC_ROOT"):
    STATIC_ROOT = os.getenv("STATIC_ROOT")
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # OAuth2, JWT
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT', 'Bearer'),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=25),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=3),
    'ROTATE_REFRESH_TOKENS': True,
    "SIGNING_KEY": os.getenv("JWT_SIGNING_KEY", SECRET_KEY),
}

FLUSH_EXPIRED_TOKEN_INTERVAL_HOURS = int(os.getenv("FLUSH_EXPIRED_TOKEN_PERIOD_HOURS", 24))
DELETE_INACTIVE_CARTS_PERIOD_DAYS = int(os.getenv("DELETE_INACTIVE_CARTS_PERIOD_DAYS", 1))

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS").split(",")

if os.getenv("CSRF_TRUSTED_ORIGINS", ""):
    CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

CORS_ORIGIN_WHITELIST = os.getenv("CORS_ORIGIN_WHITELIST").split(",")

CORS_ALLOW_CREDENTIALS = True

SESSION_COOKIE_NAME = "users-sessionid"

# Twilio Settings
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SERVICE_SID_CHANGE_EMAIL = os.getenv("TWILIO_SERVICE_SID_CHANGE_EMAIL")
TWILIO_SERVICE_SID_SIGNUP_CONFIRMATION = os.getenv("TWILIO_SERVICE_SID_SIGNUP_CONFIRMATION")
TWILIO_SERVICE_SID_PASSWORD_RESET = os.getenv("TWILIO_SERVICE_SID_PASSWORD_RESET")

# AMPQ settings
AMPQ_CONNECTION_URL = os.getenv("AMPQ_CONNECTION_URL")
PRODUCT_CRUD_EXCHANGE_TOPIC_NAME = os.getenv("PRODUCT_CRUD_EXCHANGE_TOPIC_NAME")
USERS_DATA_CRUD_EXCHANGE_TOPIC_NAME = os.getenv("USERS_DATA_CRUD_EXCHANGE_TOPIC_NAME")
ORDER_PROCESSING_EXCHANGE_TOPIC_NAME = os.getenv("ORDER_PROCESSING_EXCHANGE_TOPIC_NAME")
