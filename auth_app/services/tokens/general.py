from typing import NamedTuple

from fastapi import HTTPException, status

from auth_app.services.tokens.jwt import (
    base_decode,
    decode_token,
)


class TokenData(NamedTuple):
    token: str
    payload: dict


def requre_expired(token: str) -> TokenData:
    payload = base_decode(token=token)
    return TokenData(token=token, payload=payload)


def requre_token(token: str) -> TokenData:
    payload = decode_token(token=token)
    return TokenData(token=token, payload=payload)


def verify_refresh(token: str) -> TokenData:
    token, payload = requre_token(token)
    if payload.get("token_type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type. Refresh token required.",
        )
    return TokenData(token=token, payload=payload)


def verify_access(token: str) -> TokenData:
    token, payload = requre_token(token)
    if payload.get("token_type") != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type. Access token required.",
        )
    return TokenData(token=token, payload=payload)


def verify_admin(token: str) -> TokenData:
    token, payload = requre_token(token)
    if payload.get("role") == "USER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role type. Admin required.",
        )
    return TokenData(token=token, payload=payload)
