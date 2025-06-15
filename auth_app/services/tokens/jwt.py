import time
from datetime import datetime

import jwt
from fastapi import HTTPException, status
from jwt import (
    DecodeError,
    InvalidSignatureError,
)

from auth_app.config import settings
from auth_app.schemes.tokens import CreateData


def get_refresh_response(token: str, payload: dict) -> dict:
    return {
        "refresh_token": token,
        "payload": payload,
    }


def get_access_response(token: str) -> dict:
    return {
        "access_token": token,
    }


def generate_refresh(
    create_data: CreateData,
) -> dict:
    secret = settings.ADMIN_SECRET.get_secret_value()
    if create_data.role != "USER" and create_data.admin_secret != secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid admin secret',
        )
    payload = {
        "user_id": create_data.user_id,
        "email": create_data.email,
        "role": create_data.role,
        "expires": time.time() + settings.REFRESH_LASTING,
        "token_type": "refresh",
    }
    token = jwt.encode(
        payload=payload,
        key=settings.KEY.get_secret_value(),
        algorithm=settings.ALGORITHM.get_secret_value(),
    )
    return get_refresh_response(token, payload)


def base_decode(token: str) -> dict:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM.get_secret_value()],
        )
        return payload

    except InvalidSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Signature",
        ) from e
    except DecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Impossible to decode",
        ) from e


def decode_token(token: str) -> dict:
    payload = base_decode(token)

    if datetime.utcnow() > datetime.utcfromtimestamp(payload['expires']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Expired token',
        )
    return payload


def generate_access(refresh_token: str) -> dict[str, str]:
    payload = decode_token(token=refresh_token)
    token_type = payload.get("token_type")
    if token_type != "refresh":
        raise ValueError(f"Invalid token type: {token_type}")
    access_payload = {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "role": payload.get("role"),
        "expires": time.time() + settings.ACCESS_LASTING,
        "token_type": "access",
    }
    access_token = jwt.encode(
        payload=access_payload,
        key=settings.KEY.get_secret_value(),
        algorithm=settings.ALGORITHM.get_secret_value(),
    )
    return get_access_response(access_token)
