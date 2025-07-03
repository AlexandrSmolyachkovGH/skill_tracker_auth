import pytest
from fastapi.security import HTTPAuthorizationCredentials

from auth_app.exeptions.custom import TokenError
from auth_app.services.utils.token_handler import (
    TokenData,
    get_current_token_payload,
    token_handler,
)


def test_get_current_token_payload(
    refresh_tokens_mock: dict,
) -> None:
    """
    Test successful retrieval of payload from authorization credentials
    """
    token = refresh_tokens_mock["user_refresh_mock"]
    payload = refresh_tokens_mock["user_payload_mock"]
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=token
    )
    token_data = get_current_token_payload(credentials)

    assert isinstance(token_data, TokenData)
    assert isinstance(token_data.payload, dict)
    assert token_data.token == token
    assert token_data.payload == payload


def test_requre_expired(
    refresh_tokens_mock: dict,
) -> None:
    """
    Test that the token is correctly processed and returned as TokenData
    """
    token = refresh_tokens_mock["user_refresh_mock"]
    token_data = token_handler.requre_expired(token)

    assert isinstance(token_data, TokenData)
    assert token_data.token == token


def test_requre_token(
    refresh_tokens_mock: dict,
) -> None:
    """
    Test that the token is correctly processed and returned as TokenData
    """
    token = refresh_tokens_mock["user_refresh_mock"]
    token_data = token_handler.requre_token(token)

    assert isinstance(token_data, TokenData)
    assert token_data.token == token


def test_verify_refresh(
    access_token_mock: dict,
) -> None:
    """
    Tess unsuccessful verification of the refresh token
    """
    token = access_token_mock["access_token"]

    with pytest.raises(TokenError) as invalid_token:
        token_handler.verify_refresh(token)
    assert "Invalid token type. Refresh token required." in str(
        invalid_token.value
    )


def test_verify_access(
    refresh_tokens_mock: dict,
) -> None:
    """
    Tess unsuccessful verification of the access token
    """
    token = refresh_tokens_mock["user_refresh_mock"]

    with pytest.raises(TokenError) as invalid_access:
        token_handler.verify_access(token)
    assert "Invalid token type. Access token required." in str(
        invalid_access.value
    )


def test_verify_admin(
    refresh_tokens_mock: dict,
) -> None:
    """
    Tess unsuccessful verification of the admin role
    """
    token = refresh_tokens_mock["user_refresh_mock"]

    with pytest.raises(TokenError) as verify_admin_error:
        token_handler.verify_admin(token)
    assert "Invalid role type. Admin required." in str(
        verify_admin_error.value
    )
