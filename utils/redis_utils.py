import redis
from flask import current_app as app

redis_client = None

def init_redis():
    global redis_client
    redis_client = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=app.config['REDIS_DB'])

def get_redis():
    if not redis_client:
        init_redis()
    return redis_client