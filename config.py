class Config:
    SECRET_KEY = 'Secret'
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = '10 per second'
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0

