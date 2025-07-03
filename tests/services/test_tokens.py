from typing import cast
from unittest.mock import (
    AsyncMock,
    MagicMock,
)

import pytest
from pytest_mock import MockerFixture

from auth_app.exeptions.custom import ServiceError
from auth_app.models import (
    RefreshTokenORM,
    UserORM,
)
from auth_app.schemes.tokens import RoleDataScheme
from auth_app.schemes.users import (
    AuthUserScheme,
    GetUserScheme,
)
from auth_app.services.tokens import TokenService
from auth_app.services.utils.token_handler import TokenData


@pytest.fixture
def auth_user_data_mock(
    user_orm_mock: UserORM,
) -> AuthUserScheme:
    return AuthUserScheme(
        email=user_orm_mock.email,
        password_hash=user_orm_mock.password_hash,
    )


@pytest.fixture
def generate_refresh_patch(
    mocker: MockerFixture,
    refresh_tokens_mock: dict,
) -> MagicMock:
    refresh_mock = mocker.patch(
        "auth_app.services.tokens.token_handler.generate_refresh",
        return_value={
            "refresh_token": refresh_tokens_mock["user_refresh_mock"],
            "payload": refresh_tokens_mock["user_payload_mock"],
        },
    )
    return refresh_mock


@pytest.fixture
def token_data(
    refresh_tokens_mock: dict,
) -> TokenData:
    token_data = TokenData(
        token=refresh_tokens_mock["user_refresh_mock"],
        payload=refresh_tokens_mock["user_payload_mock"],
    )
    return token_data


@pytest.fixture
def requre_expired_patch(
    mocker: MockerFixture,
    token_data: TokenData,
) -> MagicMock:
    requre_expired = mocker.patch(
        "auth_app.services.tokens.token_handler.requre_expired",
        return_value=token_data,
    )
    return requre_expired


@pytest.fixture
def authenticate_user_patch(
    mocker: MockerFixture,
    get_user_scheme_mock: GetUserScheme,
) -> AsyncMock:
    auth_mock = mocker.patch(
        "auth_app.services.tokens.authenticate_user",
        new_callable=AsyncMock,
        return_value=get_user_scheme_mock,
    )
    return auth_mock


@pytest.fixture
def authenticate_user_failure_patch(
    mocker: MockerFixture,
) -> AsyncMock:
    auth_mock = mocker.patch(
        "auth_app.services.tokens.authenticate_user",
        new_callable=AsyncMock,
        return_value=None,
    )
    return auth_mock


@pytest.mark.asyncio
async def test_get_refresh_token(
    auth_user_data_mock: AuthUserScheme,
    authenticate_user_patch: AsyncMock,
    refresh_orm_mock: RefreshTokenORM,
    mock_token_service: TokenService,
) -> None:
    """
    Test refresh token retrieval and authentication call
    """
    mock_token_service.token_repo.get_refresh = cast(  # type: ignore[method-assign]
        AsyncMock,
        mock_token_service.token_repo.get_refresh,
    )
    mock_token_service.token_repo.get_refresh.return_value = refresh_orm_mock
    res = await mock_token_service.get_refresh_token(auth_user_data_mock)

    authenticate_user_patch.aassert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_refresh_token(
    auth_user_data_mock: AuthUserScheme,
    authenticate_user_patch: AsyncMock,
    generate_refresh_patch: MagicMock,
    mock_token_service: TokenService,
    refresh_orm_mock: dict,
) -> None:
    """
    Test successful creation and validation of a refresh token
    """
    mock_token_service.token_repo.get_refresh = cast(  # type: ignore[method-assign]
        AsyncMock,
        mock_token_service.token_repo.get_refresh,
    )
    mock_token_service.token_repo.get_refresh.return_value = None
    mock_token_service.token_repo.create_refresh = cast(  # type: ignore[method-assign]
        AsyncMock,
        mock_token_service.token_repo.create_refresh,
    )
    mock_token_service.token_repo.create_refresh.return_value = (
        refresh_orm_mock
    )
    role_auth_data = RoleDataScheme(
        **auth_user_data_mock.model_dump(),
    )
    res = await mock_token_service.create_refresh_token(role_auth_data)

    authenticate_user_patch.aassert_called_once()
    generate_refresh_patch.aassert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_refresh_token_failure(
    auth_user_data_mock: AuthUserScheme,
    authenticate_user_failure_patch: AsyncMock,
    mock_token_service: TokenService,
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
    mock_token_service: TokenService,
    refresh_orm_mock: dict,
    requre_expired_patch: MagicMock,
    token_data: TokenData,
) -> None:
    """
    Test successful exchange of a refresh token
    """
    mock_token_service.token_repo.update_refresh = cast(  # type: ignore[method-assign]
        AsyncMock,
        mock_token_service.token_repo.update_refresh,
    )
    mock_token_service.token_repo.update_refresh.return_value = (
        refresh_orm_mock
    )
    res = await mock_token_service.exchange_refresh_token(
        token_data=token_data,
    )

    requre_expired_patch.assert_called_once()
    assert isinstance(res, RefreshTokenORM)


@pytest.mark.asyncio
async def test_create_access_token(
    mock_token_service: TokenService,
    verified_user_orm_mock: UserORM,
    token_data: TokenData,
) -> None:
    """
    Test successful creation of an access token
    """
    mock_token_service.user_repo.get_user = cast(  # type: ignore[method-assign]
        AsyncMock,
        mock_token_service.user_repo.get_user,
    )
    mock_token_service.user_repo.get_user.return_value = verified_user_orm_mock
    res = await mock_token_service.create_access_token(
        token_data=token_data,
    )

    assert isinstance(res, dict)


@pytest.mark.asyncio
async def test_create_access_token_failure(
    mock_token_service: TokenService,
    user_orm_mock: UserORM,
    token_data: TokenData,
) -> None:
    """
    Test unsuccessful creation of an access token
    """
    with pytest.raises(ServiceError) as verification_error:
        mock_token_service.user_repo.get_user = cast(  # type: ignore[method-assign]
            AsyncMock,
            mock_token_service.user_repo.get_user,
        )
        mock_token_service.user_repo.get_user.return_value = user_orm_mock
        await mock_token_service.create_access_token(
            token_data=token_data,
        )

    assert "User must be verified" in str(verification_error.value)
