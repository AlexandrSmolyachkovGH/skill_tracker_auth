import random
from email.message import EmailMessage
from string import ascii_letters, digits

import aiosmtplib

from auth_app.config import settings


def generate_otp(length: int = 6) -> str:
    """
    Generate simple OTP
    """
    characters = ascii_letters + digits
    otp = ''.join(random.choices(characters, k=length))
    return otp


async def send_confirmation_email(email_to: str) -> None:
    """
    User verification via OTP
    """
    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = email_to
    message["Subject"] = "User verification"
    otp = generate_otp()
    message.set_content(
        f"Your verification OTP is: {otp}\n"
        f"This code will be active only for 5 min"
    )
    # async with aiosmtplib.SMTP(...)
