"""
Django settings for Evaluator project.
"""

from pathlib import Path
import os

if not os.getenv("IN_PRODUCTION"):
    # Load settings variables from local .env file
    from dotenv import load_dotenv
    load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS").split(",")

# Application definition

INSTALLED_APPS = (
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'django.contrib.admindocs',

    # Third party apps
    'django_extensions', 
    'rest_framework',
    # 'django_nose',
    # 'debug_toolbar',

    # Local apps
    'tables',
    'PSM',
    'upload',
    'layers',
    'map',
    'jobs',
    'first_page',
    'regions'
)

# ERRORS:
# ?: (admin.E408) 'django.contrib.auth.middleware.AuthenticationMiddleware' must be in MIDDLEWARE in order to use the admin application.
# ?: (admin.E409) 'django.contrib.messages.middleware.MessageMiddleware' must be in MIDDLEWARE in order to use the admin application.
# ?: (admin.E410) 'django.contrib.sessions.middleware.SessionMiddleware' must be in MIDDLEWARE in order to use the admin application.
#         HINT: Insert 'django.contrib.sessions.middleware.SessionMiddleware' before 'django.contrib.auth.middleware.AuthenticationMiddleware'.

# MIDDLEWARE_CLASSES = (
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
# )

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'Evaluator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    }
]

WSGI_APPLICATION = 'Evaluator.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# WhiteNoise Configuration
# http://whitenoise.evans.io/en/stable/#quickstart-for-django-apps
STATIC_URL = '/static/'
STATIC_ROOT = "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
# NOSE_ARGS = ['--nocapture']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'Evaluator.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'jobs': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'layers': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
        'map': {
            'handlers': ['file'],
            'level': 'DEBUG',
        }
    }
}

SESSION_COOKIE_AGE = 86400
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# tables.ResultsChart: (models.W042) Auto-created primary key used when not defining a primary key type, by default 'django.db.models.AutoField'.
#         HINT: Configure the DEFAULT_AUTO_FIELD setting or the AppConfig.default_auto_field attribute to point to a subclass of AutoField, e.g. 'django.db.models.BigAutoField'.

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DO not add a trailing "/"
GEOSERVER_URL = os.getenv("GEOSERVER_URL")

X_FRAME_OPTIONS = 'SAMEORIGIN'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv("DJANGO_DB_NAME"),
        'USER': os.getenv("DJANGO_DB_USER"),
        'PASSWORD': os.getenv("DJANGO_DB_PWD"),
        'HOST': os.getenv("DJANGO_DB_HOST"),
        'PORT': 5432,
        'CONN_MAX_AGE': 600,
    }
}
    
#CACHES = {
#    'default': {
#        'BACKEND':'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION':'127.0.0.1:11211',
#        'OPTIONS': {
#            'MAX_ENTRIES':1000000,
#	    'MAX_ITEM_SIZE': 100,
#	    'server_max_value_length': 1024 * 1024 * 10,
#        }
#    }
#}

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#        'LOCATION': '/var/tmp/django_cache',
#    }
#}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'evaluator_cache_table',
    }
}