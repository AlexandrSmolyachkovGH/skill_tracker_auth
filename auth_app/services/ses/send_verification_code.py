import random
from string import (
    ascii_letters,
    digits,
)

from aiobotocore.client import AioBaseClient

from auth_app.db.connect_redis import redis_client
from auth_app.messages.common import msg_creator
from auth_app.services.ses.base import (
    generate_email_payload,
    send_email,
)


def generate_otp(length: int = 6) -> str:
    """
    Generate simple OTP
    """
    characters = ascii_letters + digits
    code = ''.join(random.choices(characters, k=length))
    return code


async def send_confirmation_email(
    email_to: str,
    ses: AioBaseClient,
) -> dict:
    """
    User verification via OTP
    """
    code = generate_otp()
    msg_content = msg_creator.get_ses_confirmation_message(code)
    payload = generate_email_payload(
        message=msg_content["message"],
        subject=msg_content["subject"],
    )
    await send_email(email_to, ses, payload)
    await redis_client.set(
        name=f"otp:{email_to}",
        value=code,
        ex=300,
    )
    print("---------------------------------")
    print(f"OTP {code} was sent to {email_to}")
    print("---------------------------------")
    return {
        'message': msg_content["response_message"],
    }
