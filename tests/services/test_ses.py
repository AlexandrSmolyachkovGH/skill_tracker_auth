from unittest.mock import (
    AsyncMock,
)

import pytest
from aiobotocore.client import AioBaseClient

from auth_app.config import aws_settings
from auth_app.schemes.email import EmailPayloadScheme
from auth_app.services.ses.ses_handler import ses_handler


@pytest.fixture
def generate_email_payload_data() -> dict:
    return {
        "message": "Test message",
        "subject": "Test subject",
    }


@pytest.fixture
def send_email_patch(
    mocker,
) -> AsyncMock:
    send_email = mocker.patch(
        "auth_app.services.ses.ses_handler.ses_handler.send_email",
        new_callable=AsyncMock,
        return_value=None,
    )
    return send_email


def test_generate_email_payload(
    generate_email_payload_data,
) -> None:
    """
    Test of valid email payload creation
    """
    email_payload = ses_handler.generate_email_payload(
        **generate_email_payload_data,
    )

    assert isinstance(email_payload, EmailPayloadScheme)
    assert email_payload.message == "Test message"
    assert email_payload.subject == "Test subject"


def test_generate_verification_code() -> None:
    """
    Test of valid verification code creation
    """
    code = ses_handler.generate_otp()

    assert isinstance(code, str)
    assert len(code) == aws_settings.VERIFICATION_CODE_LENGTH


@pytest.mark.asyncio
async def test_reset_password(
    send_email_patch,
    get_user_data,
) -> None:
    """
    Test of valid password reset
    """
    result = await ses_handler.reset_password(
        email_to=get_user_data["email"],
        ses=AioBaseClient,
    )

    send_email_patch.assert_called_once()
    assert isinstance(result, dict)
    assert isinstance(result["new_password"], str)
    assert len(result["new_password"]) == aws_settings.RESET_PWD_LENGTH
    assert "Password was changed" in result["message"]


@pytest.mark.asyncio
async def test_send_confirmation_email(
    get_user_data,
    mock_redis,
    send_email_patch,
) -> None:
    """
    Test of successful sending of the confirmation email
    """
    result = await ses_handler.send_confirmation_email(
        email_to=get_user_data["email"],
        ses=AioBaseClient,
        redis_client=mock_redis,
    )

    assert isinstance(result, dict)
    assert "Verification code was sent." in result["message"]
