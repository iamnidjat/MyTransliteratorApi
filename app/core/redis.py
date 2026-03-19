import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST, # address of Redis server
    port=settings.REDIS_PORT, # port Redis is listening on
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True # helps to returns strings instead of bytes when reading from Redis
    #db=0 (by default)
)

def get_redis():
    return redis_client