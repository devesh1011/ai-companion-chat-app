import redis
from config import get_settings

settings = get_settings()

redis_host = settings.REDIS_HOST
redis_port = int(settings.REDIS_PORT)

try:
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )
    r.ping()
    print(f"Redis connected successfully to {redis_host}:{redis_port}")
except Exception as e:
    print(f"Warning: Could not connect to Redis: {str(e)}")
    r = None
