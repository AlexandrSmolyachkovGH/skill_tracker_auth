from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from auth_app.exeptions.custom import ServiceError
from auth_app.models import UserORM
from auth_app.models.users import UserRole
from auth_app.schemes.users import (
    CreateResponseScheme,
    CreateUserExtendedScheme,
    MessageResponseScheme,
    RoleEnum,
)
from auth_app.services.users import UserService

fake_user_orm = UserORM(
    id=UUID("e79229a7-b91f-475a-a88d-4f3ed6e29da4"),
    email="example@email.com",
    password_hash="$2b$12$grLAzB0SQ1WSxd84K5lei.L",
    role=UserRole.USER,
    is_verified=False,
    is_active=True,
)

payload = {
    "email": "example@email.com",
    "user_id": "e79229a7-b91f-475a-a88d-4f3ed6e29da4",
}


@pytest.mark.asyncio
async def test_create_user_record_base(user_service, mock_dependencies) -> None:
    user_data = CreateUserExtendedScheme(
        email="example@email.com",
        password_hash="1234PwdExample!",
        role=RoleEnum.USER,
    )
    mock_dependencies["user_repo"].create_user.return_value = fake_user_orm
    user_orm = await user_service.create_user_record(
        user_data=user_data,
    )
    assert isinstance(user_orm, UserORM)
    assert user_orm.role == RoleEnum.USER
    assert user_orm.email == "example@email.com"


@pytest.mark.asyncio
async def test_create_user_record_admin(mock_dependencies) -> None:
    admin_data = CreateUserExtendedScheme(
        email="example@email.com",
        password_hash="1234PwdExample!",
        role=RoleEnum.ADMIN,
        admin_code=None,
    )
    user_service = UserService(**mock_dependencies)
    with pytest.raises(ServiceError) as exc_info:
        await user_service.create_user_record(user_data=admin_data)
    assert "Invalid role or permission code" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_init_code_message(mocker, mock_dependencies):
    user_data = fake_user_orm
    mock_send = mocker.patch(
        "auth_app.services.users.ses_handler.send_confirmation_email",
        new_callable=AsyncMock,
    )
    mock_msg = mocker.patch(
        "auth_app.services.users.msg_creator.get_code_message",
        return_value="Code sent",
    )
    user_service = UserService(**mock_dependencies)
    response = await user_service.create_init_code_message(user_data)
    mock_send.assert_called_once_with(
        email_to="example@email.com",
        ses=mock_dependencies["ses"],
        redis_client=mock_dependencies["redis"],
    )
    mock_msg.assert_called_once_with("example@email.com")

    assert isinstance(response, CreateResponseScheme)
    assert response.record.email == "example@email.com"
    assert response.message == "Code sent"


@pytest.mark.asyncio
async def test_create_verification_code(mocker, mock_dependencies):
    mock_send_email = mocker.patch(
        "auth_app.services.ses.ses_handler.SesHandler.send_confirmation_email",
        new_callable=AsyncMock,
        return_value=None,
    )
    mock_get_code_message = mocker.patch(
        "auth_app.messages.common.MessageCreator.get_code_message",
        return_value="Code sent",
    )
    user_service = UserService(**mock_dependencies)
    response = await user_service.create_verification_code(
        payload=payload,
    )
    mock_send_email.assert_called_once_with(
        email_to="example@email.com",
        ses=mock_dependencies["ses"],
        redis_client=mock_dependencies["redis"],
    )
    mock_get_code_message.assert_called_once_with("example@email.com")
    assert isinstance(response, MessageResponseScheme)
    assert response.message == "Code sent"


@pytest.mark.asyncio
async def test_execute_verification(mocker, mock_dependencies) -> None:
    mock_verify_auth_code = mocker.patch(
        "auth_app.services.users.verify_auth_code",
        new_callable=AsyncMock,
        return_value=True,
    )
    mock_dependencies["user_repo"].update_user.return_value = fake_user_orm

    user_service = UserService(**mock_dependencies)
    user_data = await user_service.execute_verification(
        verification_code="123",
        payload=payload,
    )
    mock_verify_auth_code.aassert_called_once_with(
        email="example@email.com",
        code="123",
    )
    assert isinstance(user_data, UserORM)


@pytest.mark.asyncio
async def test_reset_password(mocker, mock_dependencies) -> None:
    mocker.patch(
        "auth_app.services.ses.ses_handler.SesHandler.reset_password",
        new_callable=AsyncMock,
        return_value={
            'message': "message",
            'new_password': "password",
        },
    )
    mock_dependencies["user_repo"].update_user.return_value = fake_user_orm
    user_service = UserService(**mock_dependencies)
    response = await user_service.reset_password(
        payload=payload,
    )
    assert isinstance(response, dict)
    assert response["message"] == "message"
