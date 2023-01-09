import logging
from functools import wraps
import pymongo
from pymongo.mongo_client import MongoClient

from django.conf import settings

logger = logging.getLogger(__name__)


def mongo_read_trigger(query_fn):

    @wraps(query_fn)
    def wrap(*args, **kwargs):

        kwargs['mongo_cnx'] = mongo_read_conn_get()
        result = query_fn(*args, **kwargs)

        return result

    return wrap


# set mongo read connect
mongo_r_cnx = None


def mongo_read_conn():
    global mongo_r_cnx
    _mongo_conn_set = settings.MONGO_DB_READ
    try:
        mongo_r_cnx = MongoClient(
            host=_mongo_conn_set['host'],
            port=_mongo_conn_set['port'], connect=True, serverSelectionTimeoutMS=3000,
            replicaSet=_mongo_conn_set['replicaset'],
            read_preference=pymongo.read_preferences.ReadPreference.SECONDARY_PREFERRED,
            w=1)
        mongo_r_cnx[_mongo_conn_set['authentication_source']].authenticate(
            _mongo_conn_set['user'], _mongo_conn_set['password'])

    except Exception as e:
        logger.exception('connect mongo read error')


def mongo_read_conn_get():
    global mongo_r_cnx
    if mongo_r_cnx is None:
        logger.warning('mongo read conn is None')
        mongo_read_conn()

    return mongo_r_cnx
