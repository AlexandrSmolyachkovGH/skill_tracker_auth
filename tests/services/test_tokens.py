from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest

from auth_app.exeptions.custom import ServiceError
from auth_app.models import RefreshTokenORM
from auth_app.schemes.tokens import RoleDataScheme
from auth_app.schemes.users import (
    AuthUserScheme,
)
from auth_app.services.utils.token_handler import TokenData


@pytest.fixture
def auth_user_data_mock(
    user_orm_mock,
) -> AuthUserScheme:
    return AuthUserScheme(
        email=user_orm_mock.email,
        password_hash=user_orm_mock.password_hash,
    )


@pytest.fixture
def generate_refresh_patch(
    mocker,
    refresh_tokens_mock,
) -> MagicMock:
    refresh_mock = mocker.patch(
        "auth_app.services.tokens.token_handler.generate_refresh",
        return_value={
            "refresh_token": refresh_tokens_mock["user_refresh_mock"],
            "payload": refresh_tokens_mock["user_payload_mock"],
        }
    )
    return refresh_mock


@pytest.fixture
def token_data(
    refresh_tokens_mock,
) -> TokenData:
    token_data = TokenData(
        token=refresh_tokens_mock["user_refresh_mock"],
        payload=refresh_tokens_mock["user_payload_mock"]
    )
    return token_data


@pytest.fixture
def requre_expired_patch(
    mocker,
    token_data,
) -> MagicMock:
    requre_expired = mocker.patch(
        "auth_app.services.tokens.token_handler.requre_expired",
        return_value=token_data,
    )
    return requre_expired


@pytest.fixture
def authenticate_user_patch(
    mocker,
    get_user_scheme_mock
) -> AsyncMock:
    auth_mock = mocker.patch(
        "auth_app.services.tokens.authenticate_user",
        new_callable=AsyncMock,
        return_value=get_user_scheme_mock,
    )
    return auth_mock


@pytest.fixture
def authenticate_user_failure_patch(
    mocker,
) -> AsyncMock:
    auth_mock = mocker.patch(
        "auth_app.services.tokens.authenticate_user",
        new_callable=AsyncMock,
        return_value=None,
    )
    return auth_mock


@pytest.mark.asyncio
async def test_get_refresh_token(
    auth_user_data_mock,
    authenticate_user_patch,
    refresh_orm_mock,
    mock_token_service,

) -> None:
    """
    Test refresh token retrieval and authentication call
    """
    mock_token_service.token_repo.get_refresh.return_value = refresh_orm_mock
    res = await mock_token_service.get_refresh_token(auth_user_data_mock)

    authenticate_user_patch.aassert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_refresh_token(
    auth_user_data_mock,
    authenticate_user_patch,
    generate_refresh_patch,
    mock_token_service,
    refresh_orm_mock,
) -> None:
    """
    Test successful creation and validation of a refresh token
    """
    mock_token_service.token_repo.get_refresh.return_value = None
    mock_token_service.token_repo.create_refresh.return_value = refresh_orm_mock
    role_auth_data = RoleDataScheme(
        **auth_user_data_mock.model_dump(),
    )
    res = await mock_token_service.create_refresh_token(role_auth_data)

    authenticate_user_patch.aassert_called_once()
    generate_refresh_patch.aassert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_refresh_token_failure(
    auth_user_data_mock,
    authenticate_user_failure_patch,
    mock_token_service,
) -> None:
    """
    Test unsuccessful creation of a refresh token
    """
    with pytest.raises(ServiceError) as user_not_found:
        role_auth_data = RoleDataScheme(
            **auth_user_data_mock.model_dump(),
        )
        await mock_token_service.get_refresh_token(role_auth_data)
    assert "User not found or Invalid user data" in str(user_not_found.value)


@pytest.mark.asyncio
async def test_exchange_refresh_token(
    mock_token_service,
    refresh_orm_mock,
    requre_expired_patch,
    token_data,
) -> None:
    """
    Test successful exchange of a refresh token
    """
    mock_token_service.token_repo.update_refresh.return_value = refresh_orm_mock
    res = await mock_token_service.exchange_refresh_token(
        token_data=token_data,
    )

    requre_expired_patch.assert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_access_token(
    mock_token_service,
    verified_user_orm_mock,
    token_data,
) -> None:
    """
    Test successful creation of an access token
    """
    mock_token_service.user_repo.get_user.return_value = verified_user_orm_mock
    res = await mock_token_service.create_access_token(
        token_data=token_data,
    )

    assert isinstance(res, dict)


@pytest.mark.asyncio
async def test_create_access_token_failure(
    mock_token_service,
    user_orm_mock,
    token_data,
) -> None:
    """
    Test unsuccessful creation of an access token
    """
    with pytest.raises(ServiceError) as verification_error:
        mock_token_service.user_repo.get_user.return_value = user_orm_mock
        res = await mock_token_service.create_access_token(
            token_data=token_data,
        )

    assert "User must be verified" in str(verification_error.value)
