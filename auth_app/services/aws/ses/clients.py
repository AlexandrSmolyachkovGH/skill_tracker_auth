from typing import AsyncGenerator

from aioboto3 import Session

from auth_app.config import settings


def get_aws_session() -> Session:
    return Session()


async def get_ses_client() -> AsyncGenerator:
    session = get_aws_session()
    async with session.client(
        "ses",
        endpoint_url=settings.AWS_ENDPOINT,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_DEFAULT_REGION,
    ) as client:
        yield client
