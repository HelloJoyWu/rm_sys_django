"""
Django settings for DEBUG version
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=-v4#i5r9can0c4o%$$!^n&!2(t30p48u_kp8%nt__bmv^i-6t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# When DEBUG=False and AdminEmailHandler is configured in LOGGING,
# Django emails these people the details of exceptions raised in the request/response cycle
# ADMINS = [('rmpeter0474', 'rmpeter0474@adcrow.tech')]

ALLOWED_HOSTS = [
    '.localhost', '127.0.0.1', '[::1]', '10.30.3.52', '10.9.34.19', '156.242.9.250'
]

INTERNAL_IPS = [
    '127.0.0.1', '10.30.3.52', '10.9.34.19'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_api_key',
    'django_extensions',
    'risk',
    'api',
    # allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # google provider
    'allauth.socialaccount.providers.google',
    'channels',
    'ws',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# for django-allauth
SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Point to custom account adapter.
ACCOUNT_ADAPTER = 'rmsys.adapter.SignUpAccountAdapter'

# allow signups.
ACCOUNT_ALLOW_SIGNUPS = True

ALLOW_SIGNUP_GOOGLE_HOST = ['adcrow.tech']

ROOT_URLCONF = 'rmsys.urls'

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

WSGI_APPLICATION = 'rmsys.wsgi.application'
ASGI_APPLICATION = 'rmsys.asgi.application'

# redirect to url after login when applying built-in auth

LOGIN_REDIRECT_URL = '/risk/slot'

LOGOUT_REDIRECT_URL = '/login'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'daSystem',
        'USER': 'IMwindcon_keep',
        'PASSWORD': 'Lei7YtsAb_ship',
        'HOST': '10.30.2.144',
        'PORT': 3306,
        'OPTIONS': {
            'time_zone': '+00:00',
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    },
    'maria_read': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'cypress',
        'USER': 'IMkumquat_keep',
        'PASSWORD': 'G2vi7A6Sx_ship',
        'HOST': '10.30.2.145',
        'PORT': 3306,
        'OPTIONS': {
            'time_zone': '+00:00',
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    },
    'mareport_read': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'MaReport',
        'USER': 'IMkumquat_keep',
        'PASSWORD': 'G2vi7A6Sx_ship',
        'HOST': '10.30.2.145',
        'PORT': 3306,
        'OPTIONS': {
            'time_zone': '+00:00',
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    },
    'default_read': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'daSystem',
        'USER': 'IMkumquat_keep',
        'PASSWORD': 'G2vi7A6Sx_ship',
        'HOST': '10.30.2.145',
        'PORT': 3306,
        'OPTIONS': {
            'time_zone': '+00:00',
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    },
}

DATABASE_ROUTERS = ['rmsys.dbrouter.DatabaseRouter']

MONGO_DB_READ = {
    'host': ['10.30.2.114', '10.30.2.115', '10.30.2.116'],
    'port': 27017,
    'user': 'JMkumquat_keep',
    'password': 'eWjV89SxC_ship',
    'replicaset': 'INT-CUBE_rep',
    'authentication_source': 'admin',
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/static'

# settings for default superuser
# https://docs.djangoproject.com/en/3.0/ref/django-admin/#django-admin-createsuperuser
# use this setting with "python manage.py createsuperuser --noinput"
DJANGO_SUPERUSER_USERNAME = 'admin'

DJANGO_SUPERUSER_EMAIL = 'rmpeter0474@mtopv.com'

DJANGO_SUPERUSER_PASSWORD = 'admin'

# AAD powerBI embed setting
AAD_SET = {
    # Can be set to 'MasterUser' or 'ServicePrincipal'
    'AUTHENTICATION_MODE':  'ServicePrincipal',

    # Id of the Azure tenant in which AAD app and Power BI report is hosted.
    # Required only for ServicePrincipal authentication mode.
    'TENANT_ID': 'bacfc5c4-928e-4b39-9451-0b95b149839c',

    # Client Id (Application Id) of the AAD app
    # embeded_report 7e80ddc8-7454-417a-9cd4-8df029654d4d ServicePrincipal
    # bbin_embeded_report 04038421-33ca-4438-95f5-53294dc6d80e MasterUser
    'CLIENT_ID': '7e80ddc8-7454-417a-9cd4-8df029654d4d',

    # Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
    'CLIENT_SECRET': '2i6A~76LLG.9V-bc6XOk-4n2V-n-b6b.cJ',

    # Scope of AAD app.
    # Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
    # 'https://analysis.windows.net/powerbi/api/.default'
    'SCOPE': ['https://analysis.windows.net/powerbi/api/.default'],

    # URL used for initiating authorization request
    # 'https://login.microsoftonline.com/organizations'
    # 'https://login.windows.net/mtopv1.onmicrosoft.com'
    'AUTHORITY': 'https://login.windows.net/mtopv1.onmicrosoft.com',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple':
            {'format': '[%(asctime)s] %(name)s - %(levelname)s - %(message)s'},
        'rich_console':
            {'format': '%(message)s'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'info_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': './log/info.log',
            'maxBytes': 20971520,  # 20MB
            'backupCount': 20,
            'encoding': 'utf8'
            },
        'error_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'simple',
            'filename': './log/error.log',
            'maxBytes': 20971520,  # 20MB
            'backupCount': 20,
            'encoding': 'utf8'
        },
        'rich_console': {
            'class': 'rich.logging.RichHandler',
            'level': 'DEBUG',
            'formatter': 'rich_console',
            'rich_tracebacks': True,
            'tracebacks_show_locals': True
        },
    },
    'loggers': {
        'django': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'rmsys': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'api': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'dao': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'ws': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
        'level': 'DEBUG',
    },
}
