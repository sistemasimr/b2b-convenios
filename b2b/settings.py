from datetime import timedelta
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = True

AUTH_USER_MODEL = 'users.User'
AUTH_PROFILE_MODULE = 'users.User'

ACCOUNT_AUTHENTICATION_METHOD = 'documento'
ACCOUNT_USERNAME_REQUIRED = False

LOGIN_URL = 'login/'

LOGOUT_REDIRECT_URL = '/login'

LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = [
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    #librerias
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework',
    'drf_yasg',

    #apps
    'apps.agreement',
    'apps.company',
    'apps.customers',
    'apps.users',

]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'b2b.custom_authentication_middleware.CustomAuthenticationMiddleware',

]

#CORS_ORIGIN_ALLOW_ALL = True

#CORS_ALLOWED_ORIGINS = [
#    "http://localhost:3000",
#    "http://127.0.0.1:9000",
#    "http://192.168.1.116",
#]


ROOT_URLCONF = 'b2b.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':  [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'b2b.wsgi.application'
ASGI_APPLICATION = "b2b.routing.application"

# Enrutador de bases de datos

# Carga máxima de archivos
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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

# Django rest framework config

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=45),
}

CACHES = {
   'default': {
      'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
      'LOCATION': '127.0.0.1:11211',
   }
}

# Application definition
SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'api.drf_yasg_examples.SwaggerAutoSchema',
    'SECURITY_DEFINITIONS': {
        'basic': {
            'type': 'basic'
        }
    },
    "JSON_EDITOR" : True,
    # "DOC_EXPANSION" : "full",
    "LOGIN_URL" : 'rest_framework:login',
    "LOGOUT_URL" : 'rest_framework:logout',
    "DEFAULT_MODEL_RENDERING":"example"
    # "OPERATIONS_SORTER" : "method",
}


# Email config
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'bigjohnsistemas@gmail.com'
# EMAIL_HOST_PASSWORD = 'Bigjohn2020*bj*'
EMAIL_HOST_PASSWORD = 'dkkkwfrsabgavlou'

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

X_FRAME_OPTIONS = 'SAMEORIGIN'

try:
    from .local_settings import *
except ImportError:
    raise Exception("el archivo local_settings.py es requerido para la ejecucion del projecto")