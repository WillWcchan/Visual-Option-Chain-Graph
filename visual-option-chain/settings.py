"""
Django settings for visual-option-chain project.

Generated by 'django-admin startproject' using Django 1.11.29.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/
SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = True

# 18.223.169.139
ALLOWED_HOSTS = ["*"]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR,"static"),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
STATIC_URL = '/static/'

# Deployment - provides a convenience management command to gather static files in a single directory to serve them easily
STATIC_ROOT = "/var/www/visual-option-chain.com/static/"

DEFAULT_FROM_EMAIL = 'willwcchan@gmail.com'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'livereload',
    'django.contrib.staticfiles',
    'visual-option-chain',
    'mathfilters',
    'clear_cache',
]

# Source: https://github.com/tjwalch/django-livereload-server
# LiveReloadSript to look for changes in the html,css,js files
# Start the livereload server: python manage.py livereload 
MIDDLEWARE = [
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'livereload.middleware.LiveReloadScript',
]

ROOT_URLCONF = 'visual-option-chain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'visual-option-chain/templates')],
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

WSGI_APPLICATION = 'visual-option-chain.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
# https://wsvincent.com/django-docker-postgresql/
if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD':'',
            'HOST': 'localhost', # set in docker-compose.yml
            'PORT': 5432,  # default postgres port,
            # https://docs.djangoproject.com/en/3.0/ref/settings/#test
            'TEST': {
                'NAME': 'test_database'
            },
            'CONN_MAX_AGE':5
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR , 'db.sqlite3'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# https://stackoverflow.com/questions/47585583/the-number-of-get-post-parameters-exceeded-settings-data-upload-max-number-field
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240  # higher than the count of fields

# Set up logging
# Source: https://docs.djangoproject.com/en/3.0/topics/logging/
# Prevent duplicate logging: https://stackoverflow.com/questions/6722479/why-does-my-django-1-3-logging-setup-cause-all-messages-to-be-output-twice
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'loggers': {
        'optionchain': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['file','console'],
        'level': 'INFO',
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log.log',
            'formatter': 'standard',
        },
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
}

# Redis related properties
# Source: https://realpython.com/caching-in-django-with-redis/
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_TIMEOUT': 5,
            'SOCKET_CONNECT_TIMEOUT': 5,
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
            "KEY_PREFIX": "voc"
        }
    }
}

# celery
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'


# Source: https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html#django-first-steps
# Source: https://learndjango.com/tutorials/django-email-contact-form
# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' # new
DEFAULT_FROM_EMAIL = 'willwcchan@gmail.com'
EMAIL_HOST = 'smtp.sendgrid.net' # new
EMAIL_HOST_USER = 'apikey' # new
EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
EMAIL_PORT = 587 # new
EMAIL_USE_TLS = True  # new

# Email to admin when server encounters errors
# Source: https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-ADMINS
ADMINS = [('Will', 'willwcchan@gmail.com')]
MANAGERS = [('Will', 'willwcchan@gmail.com')]
SERVER_MAIL = 'visual-option-chain-graph@localhost'

# Deployment related variables
SECURE_HSTS_SECONDS = 0
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'