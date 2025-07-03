from unittest.mock import AsyncMock, MagicMock

import pytest

from auth_app.exeptions.custom import (
    ServiceError,
    UserVerificationError,
)
from auth_app.messages.common import msg_creator
from auth_app.models import UserORM
from auth_app.schemes.users import (
    CreateResponseScheme,
    GetUserScheme,
    MessageResponseScheme,
    RoleEnum,
)


@pytest.fixture
def send_confirmation_email_mock(
    mocker,
) -> MagicMock:
    confirmation_email_mock = mocker.patch(
        "auth_app.services.users.ses_handler.send_confirmation_email",
        new_callable=AsyncMock,
        return_value={
            "message": "message"
        }
    )
    return confirmation_email_mock


@pytest.fixture
def ses_reset_pwd_mock(
    mocker,
) -> None:
    mocker.patch(
        "auth_app.services.users.ses_handler.reset_password",
        new_callable=AsyncMock,
        return_value={
            'message': msg_creator.get_reset_pwd_message(),
            'new_password': "new_password",
        }
    )


@pytest.mark.asyncio
async def test_create_user_record_base(
    mock_user_service,
    user_orm_mock,
    valid_user_creation_data,
) -> None:
    """
    Test user creation with role USER and valid data
    """
    mock_user_service.user_repo.create_user.return_value = user_orm_mock
    user_orm = await mock_user_service.create_user_record(
        user_data=valid_user_creation_data,
    )
    assert isinstance(user_orm, UserORM)
    assert user_orm.role == RoleEnum.USER
    assert user_orm.email == "email@example.com"


@pytest.mark.asyncio
async def test_create_user_record_admin(
    mock_user_service,
    invalid_admin_creation_data,
) -> None:
    """
    Test user creation with an invalid admin code for the ADMIN role
    """
    with pytest.raises(ServiceError) as exc_info:
        await mock_user_service.create_user_record(
            user_data=invalid_admin_creation_data,
        )

    assert "Invalid role or permission code" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_init_code_message(
    user_orm_mock,
    mock_user_service,
    send_confirmation_email_mock,
    mock_message_creator,
) -> None:
    """
    Test message creation with initialization code and response structure
    """
    response = await mock_user_service.create_init_code_message(user_orm_mock)

    send_confirmation_email_mock.assert_awaited_once()
    mock_message_creator.assert_called_once_with(user_orm_mock.email)
    assert isinstance(response, CreateResponseScheme)
    assert response.record.email == user_orm_mock.email
    assert response.message == "Code sent"
    assert isinstance(response.record, GetUserScheme)


@pytest.mark.asyncio
async def test_create_verification_code(
    mock_user_service,
    refresh_user_payload,
    send_confirmation_email_mock,
    mock_message_creator,
) -> None:
    """
    Test verification code creation and response structure
    """
    response = await mock_user_service.create_verification_code(
        payload=refresh_user_payload,
    )

    send_confirmation_email_mock.assert_called_once()
    mock_message_creator.assert_called_once_with(refresh_user_payload["email"])
    assert isinstance(response, MessageResponseScheme)
    assert response.message == "Code sent"


@pytest.mark.asyncio
async def test_execute_verification_success(
    mock_user_service,
    verified_user_orm_mock,
    refresh_user_payload,
    verification_code,
) -> None:
    """
    Test successful execution of the verification
    """
    mock_user_service.user_repo.update_user.return_value = verified_user_orm_mock
    user_data = await mock_user_service.execute_verification(
        verification_code=verification_code,
        payload=refresh_user_payload,
    )

    assert isinstance(user_data, UserORM)
    assert user_data.is_verified


@pytest.mark.asyncio
async def test_execute_verification_failure(
    mock_user_service,
    verified_user_orm_mock,
    refresh_user_payload,
    verification_code,
) -> None:
    """
    Test unsuccessful execution of the verification
    """
    mock_user_service.redis.get.return_value = "WrongCode"
    with pytest.raises(UserVerificationError) as exc_info:
        mock_user_service.user_repo.update_user.return_value = verified_user_orm_mock
        await mock_user_service.execute_verification(
            verification_code=verification_code,
            payload=refresh_user_payload,
        )

    assert "The user is not verified or verification failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_reset_password(
    mock_user_service,
    refresh_user_payload,
    user_orm_mock,
    ses_reset_pwd_mock,
) -> None:
    """
    Test successful execution of the password reset
    """
    mock_user_service.user_repo.update_user.return_value = user_orm_mock
    response = await mock_user_service.reset_password(
        payload=refresh_user_payload,
    )

    assert isinstance(response, dict)
    assert response["message"] == "Password was changed. Check your email to get it."
