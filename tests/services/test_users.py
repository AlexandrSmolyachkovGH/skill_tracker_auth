from unittest.mock import AsyncMock

import pytest

from auth_app.exeptions.custom import (
    ServiceError,
    UserVerificationError,
)
from auth_app.models import UserORM
from auth_app.schemes.users import (
    CreateResponseScheme,
    GetUserScheme,
    MessageResponseScheme,
    RoleEnum,
)


@pytest.mark.asyncio
async def test_create_user_record_base(
    mock_user_service,
    get_user_orm,
    valid_user_creation_data,
) -> None:
    """
    Test user creation with role USER and valid data
    """
    mock_user_service.user_repo.create_user.return_value = get_user_orm
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
    get_user_orm,
    mock_user_service,
    mock_ses_handler,
    mock_message_creator,
) -> None:
    """
    Test message creation with initialization code and response structure
    """
    response = await mock_user_service.create_init_code_message(get_user_orm)
    mock_ses_handler["mock_send_email"].assert_awaited_once()
    mock_message_creator.assert_called_once_with(get_user_orm.email)

    assert isinstance(response, CreateResponseScheme)
    assert response.record.email == get_user_orm.email
    assert response.message == "Code sent"
    assert isinstance(response.record, GetUserScheme)


@pytest.mark.asyncio
async def test_create_verification_code(
    mock_user_service,
    refresh_user_payload,
    mock_ses_handler,
    mock_message_creator,
) -> None:
    """
    Test verification code creation and response structure
    """
    response = await mock_user_service.create_verification_code(
        payload=refresh_user_payload,
    )
    mock_ses_handler["mock_send_email"].assert_called_once()
    mock_message_creator.assert_called_once_with(refresh_user_payload["email"])
    assert isinstance(response, MessageResponseScheme)
    assert response.message == "Code sent"


@pytest.mark.asyncio
async def test_execute_verification_success(
    mocker,
    mock_user_service,
    get_verified_user_orm,
    refresh_user_payload,
    verification_code,
    mock_redis,
) -> None:
    """
    Test successful execution of the verification
    """
    mocker.patch(
        "auth_app.services.utils.verification.redis_client",
        new=mock_redis,
    )
    mock_user_service.verify_auth_code = AsyncMock(return_value=True)
    mock_user_service.user_repo.update_user.return_value = get_verified_user_orm

    user_data = await mock_user_service.execute_verification(
        verification_code=verification_code,
        payload=refresh_user_payload,
    )
    assert isinstance(user_data, UserORM)
    assert user_data.is_verified


@pytest.mark.asyncio
async def test_execute_verification_failure(
    mocker,
    mock_user_service,
    get_verified_user_orm,
    refresh_user_payload,
    verification_code,
    mock_redis,
) -> None:
    """
    Test unsuccessful execution of the verification
    """
    mocker.patch(
        "auth_app.services.utils.verification.redis_client",
        new=mock_redis,
    )
    mock_redis.get.return_value = "WrongCode"
    with pytest.raises(UserVerificationError) as exc_info:
        mock_user_service.verify_auth_code = AsyncMock(return_value=False)
        mock_user_service.user_repo.update_user.return_value = get_verified_user_orm
        await mock_user_service.execute_verification(
            verification_code=verification_code,
            payload=refresh_user_payload,
        )

    assert "The user is not verified or verification failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_reset_password(
    mocker,
    mock_user_service,
    refresh_user_payload,
    get_user_orm,
    mock_ses_handler,
) -> None:
    """
    Test successful execution of the password reset
    """
    mock_user_service.user_repo.update_user.return_value = get_user_orm
    response = await mock_user_service.reset_password(
        payload=refresh_user_payload,
    )
    assert isinstance(response, dict)
    assert response["message"] == "Password was changed. Check your email to get it."
