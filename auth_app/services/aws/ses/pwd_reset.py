from aiobotocore.client import AioBaseClient

from auth_app.services.aws.ses.base import generate_email_payload, send_email
from auth_app.services.aws.ses.send_otp_email import generate_otp


async def reset_password(email_to: str, ses: AioBaseClient) -> dict:
    """
    Generate and send a new password for the User
    """
    password = generate_otp(12)
    payload = generate_email_payload(
        message=f"Your new password: {password}",
        subject='Auth service: Password reset',
    )
    await send_email(email_to, ses, payload)
    print("---------------------------------")
    print(f"Password {password} was sent to {email_to}")
    print("---------------------------------")
    return {
        'message': 'Password was changed. Check your email to get it.',
        'new_password': password,
    }
