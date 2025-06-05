import asyncio

import aioboto3

from auth_app.config import settings
from auth_app.db.connect_redis import redis_client


async def verify_sender() -> None:
    async with aioboto3.client(
            "ses",
            endpoint_url=settings.AWS_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,

    ) as ses:
        await ses.verify_email_identity(EmailAddress="sender@example.com")
        print("Sender verified.")


asyncio.run(verify_sender())
