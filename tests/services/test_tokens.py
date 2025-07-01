from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from auth_app.models import RefreshTokenORM
from auth_app.models.users import (
    UserORM,
    UserRole,
)
from auth_app.schemes.tokens import RoleDataScheme
from auth_app.schemes.users import (
    AuthUserScheme,
    GetUserScheme,
    RoleEnum,
)
from auth_app.services.tokens import TokenService
from auth_app.services.utils.token_handler import TokenData

auth_data = AuthUserScheme(
    **{
        "email": "example@email.com",
        "password_hash": "examplePassword123!",
    }
)
refresh_orm = RefreshTokenORM(
    id=UUID("cfe82c6f-7d8c-4172-bc33-04a24a065c20"),
    user_id=UUID("8c024e52-38f2-4823-90e7-5817c8b4a7ab"),
    token="eyJhbGciOiJIUzI1NiIkpXVCJ9.eyJ1cmcmVzaCJ9.mvbiRt8fK2yiQXER-PiYdk465IdDjg0cry4",
    expires_at=datetime.now(),
)
get_user = GetUserScheme(
    **{
        "email": "example@email.com",
        "password_hash": "$2b$12$WvfCqCmMM2xN4O4d8uVTnOANVCQXg0rwtYxiTi2KT8NxYLcpwNC/O",
        "id": UUID("8c024e52-38f2-4823-90e7-5817c8b4a7ab"),
        "role": RoleEnum.USER,
        "is_verified": False,
        "is_active": True,
    }
)
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiOGMwMjRlNTItMzhmMi00ODIzLTkwZTctNTgxN2M4YjRhN2FiIiwiZW1haWwiOiJqb2UuMDEwMUBleGFtcGxlLmNvbSIsInJvbGUiOiJVU0VSIiwiZXhwaXJlcyI6MTc1MDQyMzAyOC4xNzI2NzczLCJ0b2tlbl90eXBlIjoicmVmcmVzaCJ9.mvbiRt8fK2yiQXER-PiYdk465IdDjg0NRxcKRLXcry4"

token_data = TokenData(
    token=test_token,
    payload={
        "user_id": UUID("cfe82c6f-7d8c-4172-bc33-04a24a065c20"),
        "email": "example@email.com",
        "expires": 123,
        "token_type": "refresh",
        "role": "USER",
    }
)
fake_user_orm = UserORM(
    id=UUID("e79229a7-b91f-475a-a88d-4f3ed6e29da4"),
    email="example@email.com",
    password_hash="$2b$12$grLAzB0SQ1WSxd84K5lei.L",
    role=UserRole.USER,
    is_verified=True,
    is_active=True,
)


@pytest.mark.asyncio
async def test_get_refresh_token(mocker, mock_dependencies) -> None:
    mock_dependencies["token_repo"].get_refresh.return_value = refresh_orm
    mock_authenticate_user = mocker.patch(
        "auth_app.services.tokens.authenticate_user",
        new_callable=AsyncMock,
        return_value=get_user,
    )

    token_service = TokenService(**mock_dependencies)
    res = await token_service.get_refresh_token(auth_data)

    mock_authenticate_user.aassert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_refresh_token(mocker, mock_dependencies) -> None:
    mock_authenticate_user = mocker.patch(
        "auth_app.services.tokens.authenticate_user",
        new_callable=AsyncMock,
        return_value=get_user,
    )
    mock_dependencies["token_repo"].get_refresh.return_value = None
    mock_generate_refresh = mocker.patch(
        "auth_app.services.tokens.token_handler.generate_refresh",
        return_value={
            "refresh_token": "refresh_token",
            "payload": {
                "expires": 123,
                "token_type": "refresh",
            },
        },
    )
    mock_dependencies["token_repo"].create_refresh.return_value = refresh_orm

    token_service = TokenService(**mock_dependencies)
    role_auth_data = RoleDataScheme(
        **auth_data.model_dump(),
    )
    res = await token_service.create_refresh_token(role_auth_data)

    mock_authenticate_user.aassert_called_once()
    mock_generate_refresh.aassert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_exchange_refresh_token(mocker, mock_dependencies) -> None:
    mock_requre_expired = mocker.patch(
        "auth_app.services.tokens.token_handler.requre_expired",
        return_value=token_data,
    )
    mock_dependencies["token_repo"].update_refresh.return_value = refresh_orm
    token_service = TokenService(**mock_dependencies)
    res = await token_service.exchange_refresh_token(token_data=token_data)

    mock_requre_expired.assert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_access_token(mocker, mock_dependencies) -> None:
    mock_decode_token = mocker.patch(
        "auth_app.services.tokens.token_handler.decode_token",
        return_value={
            "user_id": "8c024e52-38f2-4823-90e7-5817c8b4a7ab",
            "email": "joe.0101@example.com",
            "role": "USER",
            "expires": 1750423028.1726773,
            "token_type": "refresh"
        },
    )
    mock_dependencies["user_repo"].get_user.return_value = fake_user_orm
    token_service = TokenService(**mock_dependencies)
    res = await token_service.create_access_token(token_data=token_data)

    mock_decode_token.assert_called_with(token=test_token)
    assert isinstance(res, dict)
