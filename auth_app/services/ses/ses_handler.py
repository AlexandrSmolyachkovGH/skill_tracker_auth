import random
from string import (
    ascii_letters,
    digits,
)

from aiobotocore.client import AioBaseClient
from redis.asyncio.client import Redis

from auth_app.config import aws_settings
from auth_app.messages.common import msg_creator
from auth_app.schemes.email import EmailPayloadScheme


class SesHandler:

    def generate_email_payload(
        self,
        message: str,
        subject: str,
        source: str | None = None,
    ) -> EmailPayloadScheme:
        payload = {
            'message': message,
            'subject': subject,
        }
        if source:
            payload['source'] = source
        return EmailPayloadScheme(**payload)

    async def send_email(
        self,
        email_to: str,
        ses: AioBaseClient,
        payload: EmailPayloadScheme,
    ) -> None:
        """
        Basic email sending
        """
        await ses.send_email(
            Destination={'ToAddresses': [email_to]},
            Message={
                'Body': {
                    "Text": {
                        'Charset': 'UTF-8',
                        'Data': payload.message,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': payload.subject,
                },
            },
            Source=payload.source,
        )

    async def verify_sender(
        self,
        ses: AioBaseClient,
    ) -> None:
        await ses.verify_email_identity(EmailAddress="sender@example.com")
        print("Sender verified.")

    async def reset_password(
        self,
        email_to: str,
        ses: AioBaseClient,
    ) -> dict:
        """
        Generate and send a new password for the User
        """
        password = self.generate_otp(aws_settings.RESET_PWD_LENGTH)
        msg_content = msg_creator.get_ses_reset_pwd_message(password)
        payload = self.generate_email_payload(
            message=msg_content["message"],
            subject=msg_content["subject"],
        )
        await self.send_email(email_to, ses, payload)
        print("---------------------------------")
        print(f"Password {password} was sent to {email_to}")
        print("---------------------------------")
        return {
            'message': msg_creator.get_reset_pwd_message(),
            'new_password': password,
        }

    def generate_otp(
        self,
        length: int = aws_settings.VERIFICATION_CODE_LENGTH,
    ) -> str:
        """
        Generate simple OTP
        """
        characters = ascii_letters + digits
        code = ''.join(random.choices(characters, k=length))
        return code

    async def send_confirmation_email(
        self,
        email_to: str,
        ses: AioBaseClient,
        redis_client: Redis,
    ) -> dict:
        """
        User verification via OTP
        """
        code = self.generate_otp()
        msg_content = msg_creator.get_ses_confirmation_message(code)
        payload = self.generate_email_payload(
            message=msg_content["message"],
            subject=msg_content["subject"],
        )
        await self.send_email(email_to=email_to, ses=ses, payload=payload)
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


ses_handler = SesHandler()
