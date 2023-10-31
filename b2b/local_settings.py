from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g-5svxagwuou0mwio7d-+bsrx$kmnig23yj5v=2^tf-d#ii%@8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL=True
 
ENV = 'Local'
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if ENV == 'Local':
    DATABASES = {

        'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'b2b_convenios',
                'USER': 'root',
                'PASSWORD': 'toor',
                'HOST': '127.0.0.1',
                'PORT': '3306',
            },

    }


STATIC_URL = '/static/'


MEDIA_ROOT = os.path.join(BASE_DIR, 'commons/files/')
MEDIA_URL = '/files/'
