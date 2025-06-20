import redis.asyncio as redis

from auth_app.config import redis_settings

redis_client = redis.from_url(
    redis_settings.redis_dsn,
    decode_responses=True,
)
