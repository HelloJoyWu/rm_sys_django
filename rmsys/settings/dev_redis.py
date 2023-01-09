from .dev import *

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        # "LOCATION": "unix://:redis4SYS@/redis_conn/rm_sys_redis.sock?db=1",
        "LOCATION": "redis://:redis4SYS@10.30.3.52:3002/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://:redis4SYS@10.30.3.52:3002/1"],
        },
    },
}

if 'test' in sys.argv:

    # CACHES = {
    #     'default': {
    #         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    #     }
    # }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://:redis4SYS@10.30.3.52:3002/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    REST_FRAMEWORK = {}
