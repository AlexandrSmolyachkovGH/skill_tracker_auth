from collections.abc import AsyncGenerator

import redis.asyncio as redis
from redis.asyncio.client import Redis

from auth_app.config import redis_settings

redis_client = redis.from_url(
    redis_settings.redis_dsn,
    decode_responses=True,
)


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    client = Redis.from_url(
        redis_settings.redis_dsn,
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()
