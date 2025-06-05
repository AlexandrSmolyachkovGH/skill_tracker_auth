import random
from string import ascii_letters, digits

import aioboto3

from auth_app.config import settings
from auth_app.db.connect_redis import redis_client


def generate_otp(length: int = 6) -> str:
    """
    Generate simple OTP
    """
    characters = ascii_letters + digits
    otp = ''.join(random.choices(characters, k=length))
    return otp


async def send_confirmation_email(email_to: str) -> str:
    """
    User verification via OTP
    """
    otp = generate_otp()
    async with aioboto3.client(
            "ses",
            endpoint_url=settings.AWS_ENDPOINT,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,

    ) as ses:
        await ses.send_email(
            Destination={
                'ToAddresses': [email_to]
            },
            Message={
                'Body': {
                    "Text": {
                        'Charset': 'UTF-8',
                        'Data': (
                            f'Your verification OTP is: {otp}\n'
                            f'This code will be active only for 5 minutes.'
                        )
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': 'Test email',
                },
            },
            Source="sender@example.com",
        )
        redis_client.set(
            name=f"otp:{email_to}",
            value=otp,
            ex=300,
        )
        return otp
