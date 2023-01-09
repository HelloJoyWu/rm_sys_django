from .default import *

SECRET_KEY = 'rm-sys-unM0gmo00s0aLypiUQ5HbvNgAGaLXVdcrKMWmcd0hgS4YPdZsLquiO5jxal0BmEp17y7FXcjaYN51IEu-YEKOA'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Google all-auth signup setting
ACCOUNT_ALLOW_SIGNUPS = False

ALLOW_SIGNUP_GOOGLE_HOST = ['adcrow.tech']

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'daSystem',
        'USER': 'DAxAthena_aries',
        'PASSWORD': 'yJxcNdCF74_8AhBA',
        'HOST': '10.9.24.90',
        'PORT': 3306,
        'OPTIONS': {
            'init_command': "SET TIME_ZONE='+00:00', default_storage_engine=INNODB"
        }
    },
    'maria_read': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cypress',
        'USER': 'DAxPeter_aries',
        'PASSWORD': 'JXNH3KP6p_e8dMre',
        'HOST': '10.9.24.91',
        'PORT': 3306,
        'OPTIONS': {
            'isolation_level': 'READ UNCOMMITTED',
            'init_command': "SET TIME_ZONE='+00:00'"
        },
    },
    'mareport_read': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'MaReport',
        'USER': 'DAxPeter_aries',
        'PASSWORD': 'JXNH3KP6p_e8dMre',
        'HOST': '10.9.24.91',
        'PORT': 3306,
        'OPTIONS': {
            'isolation_level': 'READ UNCOMMITTED',
            'init_command': "SET TIME_ZONE='+00:00'"
        },
    },
    'default_read': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'daSystem',
        'USER': 'DAxPeter_aries',
        'PASSWORD': 'JXNH3KP6p_e8dMre',
        'HOST': '10.9.24.91',
        'PORT': 3306,
        'OPTIONS': {
            'isolation_level': 'READ UNCOMMITTED',
            'init_command': "SET TIME_ZONE='+00:00'"
        },
    },
    'migrate_src': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'daSystem',
        'USER': 'DAxAthena_aries',
        'PASSWORD': 'yJxcNdCF74_8AhBA',
        'HOST': '10.9.24.90',
        'PORT': 3306,
        'OPTIONS': {
            'time_zone': '+00:00',
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    },
    'migrate_dest': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'backup20220503T2.sqlite3'),
    },
}

MONGO_DB_READ = {
    'host': ['10.9.24.87', '10.9.24.88', '10.9.24.89'],
    'port': 27017,
    'user': 'DAxHermes_aries',
    'password': 'AK4EyH7Nx96_GDwz',
    'replicaset': 'pro_da_ana_rs',
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
            'backupCount': 20,
            'encoding': 'utf8'
            },
        'error_file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'simple',
            'filename': '/tmp/log/rm_sys_error.log',
            'maxBytes': 20971520,  # 20MB
            'backupCount': 20,
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
DEFAULT_FROM_EMAIL = "T2 <dabot@riskmanagement.cqgame.cc>"

ADMINS = [('rmpeter0474', 'rmpeter0474@adcrow.tech'), ]
MANAGERS = ADMINS
