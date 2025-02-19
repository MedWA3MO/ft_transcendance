import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import timedelta
import sys
import logging
from urllib.parse import urlparse

load_dotenv()
import certifi


# Replace the DATABASES section of your settings.py with this
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': 5432,
    }
}

os.environ['SSL_CERT_FILE'] = certifi.where()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# all env variables used in the project

ALL_USED_ENV_VARS = [
    "DOMAIN_NAME",
    "SECRET_KEY",
    "DEBUG",
    "OAUTH42_CLIENT_ID",
    "OAUTH42_CLIENT_SECRET",
    "OAUTH42_REDIRECT_URI",
    "OAUTH42_AUTH_URL",
    "OAUTH42_TOKEN_URL",
    "OAUTH42_USER_URL",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "DOCKER_POSTGRES_PORT",
    "DOCKER_POSTGRES_HOSTNAME",
    "DOCKER_BACKEND_PORT",
    "DOCKER_BACKEND_HOSTNAME",
    "REDIS_URL",  # Add Redis URL here
]

missing_vars = [var for var in ALL_USED_ENV_VARS if os.getenv(var) is None]

if missing_vars:
    logging.error(f"Error: The following environment variables are not set: {', '.join(missing_vars)}")
    sys.exit(1)

SECRET_KEY = os.getenv("SECRET_KEY")

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [os.getenv("REDIS_URL")],
            "symmetric_encryption_keys": [SECRET_KEY],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}


DOMAIN_NAME = os.getenv("DOMAIN_NAME")
DOCKER_REDIS_HOSTNAME="red-cu784drqf0us73e2sr2g"
DOCKER_REDIS_PORT=os.getenv('DOCKER_REDIS_PORT')
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
# Set your 42 OAuth credentials
OAUTH42_CLIENT_ID = os.getenv("OAUTH42_CLIENT_ID")
OAUTH42_CLIENT_SECRET = os.getenv("OAUTH42_CLIENT_SECRET")
OAUTH42_REDIRECT_URI = os.getenv("OAUTH42_REDIRECT_URI")
OAUTH42_AUTH_URL = os.getenv("OAUTH42_AUTH_URL")
OAUTH42_TOKEN_URL = os.getenv("OAUTH42_TOKEN_URL")
OAUTH42_USER_URL = os.getenv("OAUTH42_USER_URL")

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

database_url = os.getenv("DATABASE_URL")
if database_url:
    result = urlparse(database_url)
    POSTGRES_DB = result.path[1:]  # Remove leading '/'
    POSTGRES_USER = result.username
    POSTGRES_PASSWORD = result.password
    DOCKER_POSTGRES_HOSTNAME = result.hostname
    DOCKER_POSTGRES_PORT = result.port
else:
    POSTGRES_DB = None # Add your database name here
    POSTGRES_USER = None
    POSTGRES_PASSWORD = None
    DOCKER_POSTGRES_HOSTNAME = None
    DOCKER_POSTGRES_PORT = None
REDIS_URL = os.getenv("REDIS_URL")  # Add Redis URL here
DOCKER_BACKEND_PORT=os.getenv("DOCKER_BACKEND_PORT") #frontend will use this port to connect to backend
DOCKER_BACKEND_HOSTNAME=os.getenv("DOCKER_BACKEND_HOSTNAME") #frontend will use this hostname to connect to backend



SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # its is a https request from the client but it is forwarded to the backend as http request
# Ensure that cookies are only sent over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = [    
    "ft-transcendance-1.onrender.com",  
    "ft-transcendance-1.onrender",
    "ft-transcendance-1",  
    "ft-transcendance-wjhi.onrender",
    "ft-transcendance-wjhi.onrender.com",
    "ft-transcendance-wjhi", 
    '*', ]

PORT = os.getenv('PORT', 8000)

AUTH_USER_MODEL = "authentication.CustomUser"

AUTHENTICATION_BACKENDS = [
	"django.contrib.auth.backends.ModelBackend",
]


REST_FRAMEWORK = {
	"DEFAULT_AUTHENTICATION_CLASSES": (
		"rest_framework_simplejwt.authentication.JWTAuthentication",
	),
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    "AUTH_COOKIE": "jwt",
    "AUTH_COOKIE_SECURE": True,  # Temporarily set to False to debug
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_PATH": "/",
    "AUTH_COOKIE_SAMESITE": "None",  # Change from Strict to Lax
    "ROTATE_REFRESH_TOKENS": True,
    'BLACKLIST_AFTER_ROTATION': True,
    'SIGNING_KEY': SECRET_KEY,
    "ALGORITHM": "HS256",
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}



## Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587

DJANGO_SETTINGS_MODULE= 'core.settings'


# Create token expiry time
PASSWORD_RESET_TIMEOUT = 3600  # 1 hour in seconds

INSTALLED_APPS = [
    'corsheaders',
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pong',
    'game',
    # 'game.apps.GameConfig',
    "authentication.apps.AuthenticationConfig",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "chat",
    "connect_four",
    "core",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this at the top
    'django.middleware.security.SecurityMiddleware',
    'authentication.middleware.TokenVerificationMiddleWare',  # Move this up
    'authentication.simplemiddleware.simple_middleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'authentication.middleware.RequestLoggingMiddleware', 
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'



#images settings
MEDIA_URL = 'backend-media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CORS_ALLOWED_ORIGINS = [
    "https://ft-transcendance-1.onrender.com",
    "https://ft-transcendance-wjhi.onrender.com"
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https:\/\/.*\.onrender\.com$",
]

CORS_ALLOW_METHODS = [
	'DELETE',
	'GET',
	'OPTIONS',
	'PATCH',
	'POST',
	'PUT',
]


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "Africa/Casablanca"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/backend-static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_CREDENTIALS = True
# CORS_ALLOW_ALL_ORIGINS = True  # Keep this False for security
CORS_EXPOSE_HEADERS = ["Content-Type", "X-CSRFToken"]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'pragma',
    'cache-control',
    'if-modified-since',
    'if-none-match',
    'x-frame-options',
    'x-access-token',
    'x-refresh-token',
    'x-username',
    'x-password',
    'expires'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'authentication': {  # Replace with your app name
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}