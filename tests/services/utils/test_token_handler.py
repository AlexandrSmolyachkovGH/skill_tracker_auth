from unittest.mock import patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials

from auth_app.exeptions.custom import TokenError
from auth_app.services.utils.token_handler import (
    TokenData,
    get_current_token_payload,
    token_handler,
)
from tests.services.utils.test_jwt_handler import (
    payload,
    token,
)


def test_get_current_token_payload() -> None:
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with patch.object(token_handler, "verify_refresh") as mock_verify_refresh:
        mock_verify_refresh.return_value = TokenData(
            token=token,
            payload=payload,
        )
        token_data = get_current_token_payload(credentials)
        assert isinstance(token_data, TokenData)
        assert token_data.token == token
        assert token_data.payload == payload


def test_requre_expired() -> None:
    token_data = token_handler.requre_expired(token)
    assert isinstance(token_data, TokenData)
    assert token_data.token == token


def test_requre_token() -> None:
    with patch.object(token_handler, "decode_token") as mock_decode:
        mock_decode.return_value = token_handler.requre_expired(token)
        token_data = token_handler.requre_expired(token)
        assert isinstance(token_data, TokenData)
        assert token_data.token == token


def test_verify_refresh() -> None:
    with patch.object(token_handler, "requre_token") as mock_requre_token:
        mock_requre_token.return_value = TokenData(
            token=token,
            payload={
                "token_type": "abc",
            }
        )
        with pytest.raises(TokenError) as invalid_token:
            token_handler.verify_refresh(token)

        assert "Invalid token type. Refresh token required." in str(invalid_token.value)


def test_verify_access() -> None:
    with patch.object(token_handler, "requre_token") as mock_requre_token:
        mock_requre_token.return_value = TokenData(
            token=token,
            payload={
                "token_type": "abc",
            }
        )
        with pytest.raises(TokenError) as invalid_access:
            token_handler.verify_access(token)
        assert "Invalid token type. Access token required." in str(invalid_access.value)


def test_verify_admin() -> None:
    with patch.object(token_handler, "requre_token") as mock_requre_token:
        mock_requre_token.return_value = TokenData(
            token=token,
            payload={
                "role": "USER",
            }
        )
        with pytest.raises(TokenError) as verify_admin_error:
            token_handler.verify_admin(token)
        assert "Invalid role type. Admin required." in str(verify_admin_error.value)
