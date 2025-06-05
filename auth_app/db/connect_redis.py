import redis.asyncio as redis

from auth_app.config import settings

redis_client = redis.from_url(
    settings.redis_dsn,
    decode_responses=True,
)
