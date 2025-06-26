from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import GetUserScheme, RoleEnum
from auth_app.services.utils.authenticate_user import authenticate_user
from auth_app.services.utils.pwd_hashing import (
    hash_password,
    verify_password,
)

email = "email@example.com"
pwd = "12345Password!"
hashed_pwd = hash_password(pwd)


def test_hash_password() -> None:
    hashed_password = hash_password(pwd)
    assert isinstance(hashed_password, str)


def test_verify_password() -> None:
    assert verify_password(pwd, hashed_pwd)


@pytest.mark.asyncio
async def test_authenticate_user() -> None:
    mock_user = GetUserScheme(
        email=email,
        password_hash=hashed_pwd,
        id=UUID("150881a3-c874-4a93-92d2-6be10a4c189c"),
        role=RoleEnum.USER,
        is_verified=False,
        is_active=True,
    )
    mock_repo: UserRepo = AsyncMock(spec=UserRepo)
    mock_repo.get_users.return_value = [mock_user]
    result = await authenticate_user(email, pwd, mock_repo)
    assert isinstance(result, GetUserScheme)
