from unittest.mock import (
    AsyncMock,
    patch,
)

import pytest
from aiobotocore.client import AioBaseClient

from auth_app.config import aws_settings
from auth_app.db.connect_redis import redis_client
from auth_app.messages.common import msg_creator
from auth_app.schemes.email import EmailPayloadScheme
from auth_app.services.ses.ses_handler import ses_handler


def test_generate_email_payload() -> None:
    email_payload = ses_handler.generate_email_payload(
        message="Test message",
        subject="Test subject"
    )
    assert isinstance(email_payload, EmailPayloadScheme)
    assert isinstance(email_payload.message, str)
    assert isinstance(email_payload.subject, str)


def test_generate_otp() -> None:
    code = ses_handler.generate_otp()
    assert isinstance(code, str)
    assert len(code) == aws_settings.VERIFICATION_CODE_LENGTH


@pytest.mark.asyncio
async def test_reset_password() -> None:
    with patch.object(ses_handler, "generate_email_payload") as mock_gen_payload, \
        patch.object(ses_handler, "send_email", new_callable=AsyncMock) as mock_send_email, \
        patch.object(ses_handler, "generate_otp") as mock_generate_otp:
        mock_send_email.return_value = None
        mock_generate_otp.return_value = "TestOTP123"
        mock_gen_payload.return_value = EmailPayloadScheme(
            message="Test message",
            subject="Test subject",
            source="sender@example.com",
        )
        result = await ses_handler.reset_password(
            email_to='email_to@example.com',
            ses=AioBaseClient,
        )
        assert isinstance(result, dict)
        assert result["new_password"] == "TestOTP123"


@pytest.mark.asyncio
async def test_send_confirmation_email() -> None:
    with patch.object(ses_handler, "generate_otp") as mock_generate_otp, \
        patch.object(ses_handler, "send_email", new_callable=AsyncMock) as mock_send_email, \
        patch.object(msg_creator, "get_ses_confirmation_message") as mock_get_ses_message, \
        patch.object(redis_client, "set", new_callable=AsyncMock) as mock_set_redis:
        mock_generate_otp.return_value = "TestOTP123"
        mock_get_ses_message.return_value = {
            "message": "test message",
            "subject": "test subject",
            "response_message": "test response",
        }
        mock_send_email.return_value = None
        mock_set_redis.return_value = None
        result = await ses_handler.send_confirmation_email(
            email_to="email_to@example.com",
            ses=AioBaseClient,
            redis_client=redis_client,
        )
        assert isinstance(result, dict)
        assert isinstance(result["message"], str)
        assert result["message"] == "test response"
