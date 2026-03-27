import redis
from django.conf import settings

# Redis Connection
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


# Redis Operations
def set_key(key, value, expiry=None):
    redis_client.set(key, value, ex=expiry)


def get_key(key):
    return redis_client.get(key)


def delete_key(key):
    redis_client.delete(key)