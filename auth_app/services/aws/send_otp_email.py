import random
from string import ascii_letters, digits

from aiobotocore.client import AioBaseClient

from auth_app.db.connect_redis import redis_client


def generate_otp(length: int = 6) -> str:
    """
    Generate simple OTP
    """
    characters = ascii_letters + digits
    otp = ''.join(random.choices(characters, k=length))
    return otp


async def send_confirmation_email(email_to: str, ses: AioBaseClient) -> str:
    """
    User verification via OTP
    """
    otp = generate_otp()
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
    await redis_client.set(
        name=f"otp:{email_to}",
        value=otp,
        ex=300,
    )
    print("---------------------------------")
    print(f"OTP {otp} was sent to {email_to}")
    print("---------------------------------")
    return otp
