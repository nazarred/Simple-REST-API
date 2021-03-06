"""
Django settings for simple_api project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from configurations import Configuration, values
import dj_database_url



class Base(Configuration):

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'fbq#&dnn@p@v4p@=l_1ku8e8bpznh3#+4apl1^f+0^6=mqa%9h'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1']


    # Application definition

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'rest_framework',

        'accounts',
        'posts'

    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'simple_api.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

    WSGI_APPLICATION = 'simple_api.wsgi.application'


    # Database
    # https://docs.djangoproject.com/en/1.11/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': values.Value('django.db.backends.postgresql_psycopg2', environ_name='DJANGO_DATABASE_ENGINE'),
            'NAME': values.Value('db', environ_name='DB', environ_prefix='POSTGRES'),
            'USER': values.Value('db_user', environ_name='USER', environ_prefix='POSTGRES'),
            'PASSWORD': values.Value('db_password', environ_name='PASSWORD', environ_prefix='POSTGRES'),
            'HOST': values.Value('database', environ_name='DJANGO_DATABASE_HOST'),
            'PORT': values.Value('5432', environ_name='DJANGO_DATABASE_PORT'),
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

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True


    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.11/howto/static-files/

    STATIC_URL = '/static/'

    STATIC_ROOT = os.path.join(BASE_DIR, '..', 'staticfiles')

    MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')

    AUTH_USER_MODEL = 'accounts.User'

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        ),
    }

    ADMIN_EMAIL = 'admin-api@co.com'
    HOSTNAME = 'localhost'
    PROTOCOL = 'http'

    CELERY_BROKER_URL = values.Value('redis://localhost:6379')
    CELERY_RESULT_BACKEND = values.Value('redis://localhost:6379')
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'


class Dev(Base):
    DEBUG = True

    EMAIL_HOST = values.Value('smtp.sendgrid.net')
    EMAIL_PORT = values.Value('587')
    EMAIL_HOST_USER = values.Value('user')
    EMAIL_HOST_PASSWORD = values.Value('password')

    CLEARBIT_KEY = values.Value('xxx')
    HUNTER_API_KEY = values.Value('xxx')
    ALLOWED_HOSTS = ['localhost', '.herokuapp.com', 'ec2-18-217-34-115.us-east-2.compute.amazonaws.com']


class Prod(Base):
    DEBUG = False

    EMAIL_HOST = values.Value('smtp.sendgrid.net')
    EMAIL_PORT = values.Value('587')
    EMAIL_HOST_USER = values.Value('user')
    EMAIL_HOST_PASSWORD = values.Value('password')

    CLEARBIT_KEY = values.Value('xxx')
    HUNTER_API_KEY = values.Value('xxx')

    ALLOWED_HOSTS = ['localhost', '.herokuapp.com', 'ec2-18-217-34-115.us-east-2.compute.amazonaws.com']
    STATIC_ROOT = os.path.join(Base.BASE_DIR, 'staticfiles')
    DATABASES = Base.DATABASES.copy()
    DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

