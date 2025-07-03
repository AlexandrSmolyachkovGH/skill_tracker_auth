from unittest.mock import MagicMock

import pytest

from auth_app.schemes.users import (
    GetUserScheme,
)
from auth_app.services.utils.authenticate_user import (
    authenticate_user,
)
from auth_app.services.utils.pwd_hashing import (
    hash_password,
    verify_password,
)


def test_hash_password(
    get_user_data: dict,
) -> None:
    """
    Test that a password is hashed correctly and can be verified
    """
    hashed_password = hash_password(get_user_data["password"])

    assert isinstance(hashed_password, str)
    assert verify_password(
        plain_password=get_user_data["password"],
        hashed_password=hashed_password,
    )


def test_verify_password(
    get_user_data: dict,
) -> None:
    """
    Test successful password verification with correct password
    """
    assert verify_password(
        plain_password=get_user_data["password"],
        hashed_password=get_user_data["password_hash"],
    )


@pytest.mark.asyncio
async def test_authenticate_user(
    get_user_data: dict,
    get_user_scheme_mock: GetUserScheme,
    mock_user_repo: MagicMock,
) -> None:
    """
    Test successful authentication with valid user data
    """
    mock_user_repo.get_users.return_value = [get_user_scheme_mock]
    result = await authenticate_user(
        email=get_user_data["email"],
        password=get_user_data["password"],
        user_repo=mock_user_repo,
    )

    mock_user_repo.get_users.assert_called_once()
    assert isinstance(result, GetUserScheme)
