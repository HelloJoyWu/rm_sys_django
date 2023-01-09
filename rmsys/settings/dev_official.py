from .dev import *

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "unix:///redis_conn/sys_redis.sock?db=1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

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
    }
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

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600

if 'test' in sys.argv:

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    # REST_FRAMEWORK = {}
