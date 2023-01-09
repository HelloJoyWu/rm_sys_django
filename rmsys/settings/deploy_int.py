from .default import *

SECRET_KEY = 'rm-sys-dev-q2S_A1IKLiFMAln3ydHovq24kRHrjF1sIuxHTxWiBTE'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Google all-auth signup setting
ACCOUNT_ALLOW_SIGNUPS = True

ALLOW_SIGNUP_GOOGLE_HOST = ['adcrow.tech']

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
    'migrate_src': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'daSystem',
        'USER': 'IMkumquat_keep',
        'PASSWORD': 'Lei7YtsAb_ship',
        'HOST': '10.30.2.144',
        'PORT': 3306,
        'OPTIONS': {
            'time_zone': '+00:00',
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    },
    'migrate_dest': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'backup20220503SIT.sqlite3'),
    },
}

MONGO_DB_READ = {
    'host': ['10.30.2.114', '10.30.2.115', '10.30.2.116'],
    'port': 27017,
    'user': 'JMkumquat_keep',
    'password': 'eWjV89SxC_ship',
    'replicaset': 'INT-CUBE_rep',
    'authentication_source': 'admin',
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{"address": "/redis_conn/sys_redis.sock", "password": "redis4SYS"}],
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "unix://:redis4SYS@/redis_conn/sys_redis.sock",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'simple':
            {'format': '[%(asctime)s] %(name)s <process=%(process)d, thread=%(thread)d> %(levelname)s - %(message)s'},
        'rich_console':
            {'format': '%(message)s <process=%(process)d, thread=%(thread)d>'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
            'stream': 'ext://sys.stdout'
        },
        'info_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'filename': '/tmp/log/rm_sys_info.log',
            'maxBytes': 20971520,  # 20MB
            'backupCount': 10,
            'encoding': 'utf8'
            },
        'error_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'simple',
            'filename': '/tmp/log/rm_sys_error.log',
            'maxBytes': 20971520,  # 20MB
            'backupCount': 10,
            'encoding': 'utf8'
        },
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'ERROR',
            'filters': ['require_debug_false'],
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
        'django.server': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'rmsys': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'api': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
        'dao': {
            'handlers': ['rich_console', 'info_file_handler', 'error_file_handler', 'mail_admins'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['rich_console', 'info_file_handler', 'error_file_handler'],
        'level': 'INFO',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'dabot@adcrow.tech'
EMAIL_HOST_PASSWORD = 'uupjyfcesixutezh'
EMAIL_TIMEOUT = 5
SERVER_EMAIL = EMAIL_HOST_USER

ADMINS = [('rmpeter0474', 'rmpeter0474@adcrow.tech'), ]
MANAGERS = ADMINS
