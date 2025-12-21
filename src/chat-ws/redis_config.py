import redis
import os

redis_host = os.getenv("REDIS_HOST", "postgres-headless")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

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
