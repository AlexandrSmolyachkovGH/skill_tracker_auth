from typing import NamedTuple

from fastapi import Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from auth_app.exeptions.custom import TokenError
from auth_app.services.utils.jwt_handler import JWTHandler


class TokenData(NamedTuple):
    token: str
    payload: dict


class TokenHandler(JWTHandler):
    """
    A service for implementing operations related to token verification.
    """

    def __init__(self) -> None:
        super().__init__()
        self.oauth2_scheme = HTTPBearer()

    def requre_expired(
        self,
        token: str,
    ) -> TokenData:
        payload = self.base_decode(token=token)
        return TokenData(token=token, payload=payload)

    def requre_token(
        self,
        token: str,
    ) -> TokenData:
        payload = self.decode_token(token=token)
        return TokenData(token=token, payload=payload)

    def verify_refresh(
        self,
        token: str,
    ) -> TokenData:
        token, payload = self.requre_token(token)
        if payload.get("token_type") != "refresh":
            raise TokenError("Invalid token type. Refresh token required.")
        return TokenData(token=token, payload=payload)

    def verify_access(
        self,
        token: str,
    ) -> TokenData:
        token, payload = self.requre_token(token)
        if payload.get("token_type") != "access":
            raise TokenError("Invalid token type. Access token required.")
        return TokenData(token=token, payload=payload)

    def verify_admin(
        self,
        token: str,
    ) -> TokenData:
        token, payload = self.requre_token(token)
        if payload.get("role") == "USER":
            raise TokenError("Invalid role type. Admin required.")
        return TokenData(token=token, payload=payload)


token_handler = TokenHandler()


def get_current_token_payload(
    token: HTTPAuthorizationCredentials = Security(
        token_handler.oauth2_scheme
    ),
) -> TokenData:
    token_data = token_handler.verify_refresh(token.credentials)
    return token_data
