from typing import AsyncGenerator

from aioboto3 import Session
from aiobotocore.client import AioBaseClient

from auth_app.config import aws_settings


def get_aws_session() -> Session:
    return Session()


async def get_ses_client() -> AsyncGenerator[AioBaseClient, None]:
    session = get_aws_session()
    async with session.client(
        "ses",
        endpoint_url=aws_settings.AWS_ENDPOINT,
        aws_access_key_id=aws_settings.AWS_ACCESS_KEY_ID.get_secret_value(),
        aws_secret_access_key=aws_settings.AWS_SECRET_ACCESS_KEY.get_secret_value(),
        region_name=aws_settings.AWS_DEFAULT_REGION,
    ) as client:
        yield client
