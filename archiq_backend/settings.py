import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
from pip._internal import locations

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DJANGO_DEBUG", False)
hosts_str = os.environ.get('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = hosts_str.split()

# AWS ENV VARIABLES
AWS_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.getenv('S3_BUCKET_URL')
AWS_S3_FULL_URL = os.getenv('S3_BUCKET_FULL_URL')
AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
AWS_DEFAULT_ACL = None
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Maximum size of the request body (50MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 50485760

# Maximum number of GET/POST parameters (1000)
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# Maximum file upload size (50MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 50485760

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'phonenumber_field',
    'users',
    'location',
    'marketing',
    'support',
    'properties',
    'sales',
    'applications',
    'storages',
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CSRF, CORS, and static files settings...
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    'https://slyamgazy.kz',
    'https://api.slyamgazy.kz',
    'https://www.slyamgazy.kz',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = (
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    'https://slyamgazy.kz',
    'https://www.slyamgazy.kz',
)

from corsheaders.defaults import default_methods, default_headers

CORS_ALLOW_METHODS = list(default_methods) + [
    'OPTIONS',
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    'content-type',
    'authorization',
]

ROOT_URLCONF = 'archiq_backend.urls'
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

WSGI_APPLICATION = 'archiq_backend.wsgi.application'

AUTH_USER_MODEL = 'users.CustomUser'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv("DB_NAME"),
        'USER': os.getenv("DB_USER"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'HOST': os.getenv("DB_HOST"),
        'PORT': os.getenv("DB_PORT"),
    }
}

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

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(weeks=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(weeks=52)
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = '/static/'
STATIC_ROOT = '/app/static'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')
LLM_MODEL = os.getenv('LLM_MODEL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH')

SPECTACULAR_SETTINGS = {
    'TITLE': 'Archiq API',
    'DESCRIPTION': 'Archiq API documentation',
    'VERSION': 'v1',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    "SWAGGER_UI_SETTINGS": {
        "filter": True,
    },
    'SECURITY_SCHEMES': {
        'BearerAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer your_token"'
        }
    }
}



