# Licensed under the MIT License

"""Django settings for www.mymusichere.me."""

import os
import pathlib

from mymusichere import env


BASE_DIR = pathlib.Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = env.get_secret('mymusichere_secret_key')

DEBUG = bool(int(env.get_config('debug', '0')))

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'scores.apps.ScoresConfig',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'debug_toolbar'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'mymusichere.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'mymusichere' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mymusichere.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': env.get_config('mymusichere_db_host'),
        'NAME': env.get_secret('mymusichere_db_name'),
        'USER': env.get_secret('mymusichere_db_user'),
        'PASSWORD': env.get_secret('mymusichere_db_password'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # pylint: disable=line-too-long  # noqa: E501
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname}:{asctime}:{module}:{message}',
            'style': '{'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'mymusichere.log',
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SESSION_COOKIE_AGE = 600

STATIC_ROOT = BASE_DIR / 'static'

STATICFILES_DIRS = [
    BASE_DIR / 'mymusichere' / 'static',
]

STATIC_URL = '/static/'

MEDIA_ROOT = BASE_DIR / 'media'

MEDIA_URL = '/media/'


GITHUB_SCORES_SOURCE_REPO = 'https://github.com/dmitrvk/mymusichere'

PUBLISH_TOKEN = os.environ['PUBLISH_TOKEN']
