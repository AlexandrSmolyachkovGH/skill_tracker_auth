from aiobotocore.client import AioBaseClient

from auth_app.messages.common import msg_creator
from auth_app.services.ses.base import (
    generate_email_payload,
    send_email,
)
from auth_app.services.ses.send_verification_code import generate_otp


async def reset_password(
    email_to: str,
    ses: AioBaseClient,
) -> dict:
    """
    Generate and send a new password for the User
    """
    password = generate_otp(12)
    msg_content = msg_creator.get_ses_reset_pwd_message(password)
    payload = generate_email_payload(
        message=msg_content["message"],
        subject=msg_content["subject"],
    )
    await send_email(email_to, ses, payload)
    print("---------------------------------")
    print(f"Password {password} was sent to {email_to}")
    print("---------------------------------")
    return {
        'message': msg_creator.get_reset_pwd_message(),
        'new_password': password,
    }
