
from flask_caching import Cache as Flask_Cache
import redis

from hollowman import conf
from hollowman.log import logger

__cache_backend = Flask_Cache(config={
    'CACHE_REDIS_URL': conf.ASGARD_CACHE_URL,
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': conf.ASGARD_CACHE_KEY_PREFIX,
    'CACHE_DEFAULT_TIMEOUT': conf.ASGARD_CACHE_DEFAULT_TIMEOUT,
    'CACHE_OPTIONS': {
        'socket_connect_timeout': 5
    }
})

def get(key):
    try:
        return __cache_backend.get(key)
    except redis.exceptions.ConnectionError as e:
        logger.error({"action": "cache-get", "state": "error", "key": key, "cache-backend": __cache_backend.config.get("CACHE_REDIS_URL")})

    return None

def set(key, value, *args, **kwargs):
    try:
        return __cache_backend.set(key, value, *args, **kwargs)
    except redis.exceptions.ConnectionError as e:
        logger.error({"action": "cache-set", "state": "error", "key": key, "cache-backend": __cache_backend.config.get("CACHE_REDIS_URL")})

    return False


def init_app(application):
    __cache_backend.init_app(application)
