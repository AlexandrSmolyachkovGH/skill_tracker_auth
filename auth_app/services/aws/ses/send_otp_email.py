import random
from string import ascii_letters, digits

from aiobotocore.client import AioBaseClient

from auth_app.db.connect_redis import redis_client
from auth_app.schemes.email import EmailPayload
from auth_app.services.aws.ses.base import generate_email_payload, send_email


def generate_otp(length: int = 6) -> str:
    """
    Generate simple OTP
    """
    characters = ascii_letters + digits
    otp = ''.join(random.choices(characters, k=length))
    return otp


async def send_confirmation_email(email_to: str, ses: AioBaseClient) -> dict:
    """
    User verification via OTP
    """
    otp = generate_otp()
    payload = generate_email_payload(
        message=(
            f'Your verification OTP is: {otp}\n'
            f'This code will be active only for 5 minutes.'
        ),
        subject='Auth service: Verification code',
    )
    await send_email(email_to, ses, payload)
    # await ses.send_email(
    #     Destination={
    #         'ToAddresses': [email_to]
    #     },
    #     Message={
    #         'Body': {
    #             "Text": {
    #                 'Charset': 'UTF-8',
    #                 'Data': (
    #                     f'Your verification OTP is: {otp}\n'
    #                     f'This code will be active only for 5 minutes.'
    #                 )
    #             },
    #         },
    #         'Subject': {
    #             'Charset': 'UTF-8',
    #             'Data': 'Test email',
    #         },
    #     },
    #     Source="sender@example.com",
    # )
    await redis_client.set(
        name=f"otp:{email_to}",
        value=otp,
        ex=300,
    )
    print("---------------------------------")
    print(f"OTP {otp} was sent to {email_to}")
    print("---------------------------------")
    return {
        'message': 'Verification code was sent. Check your email to get it.',
    }
