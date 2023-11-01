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
 
ENV = 'Develop'
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if ENV == 'Develop':
    DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'b2b',
                'USER': 'root',
                'PASSWORD': 'DBimr2021intranetDB',
                'HOST': '192.168.1.21',
                'PORT': '3306',
            },

        "bigjohndb": {
            'ENGINE': 'mssql',
            'NAME': 'BIGJOHN',
            'USER': 'bigjohn',
            'PASSWORD': '2UMIrtsqCEmkv',
            'HOST': 'tcp:comerssiamirror.eastus2.cloudapp.azure.com,38693',
            'PORT': '1433',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
                'collation': 'SQL_Latin1_General_CP1_CI_AS',
                'unicode_results': True,
            },
        }
    }


STATIC_URL = '/static/'


MEDIA_ROOT = os.path.join(BASE_DIR, 'commons/files/')
MEDIA_URL = '/files/'
