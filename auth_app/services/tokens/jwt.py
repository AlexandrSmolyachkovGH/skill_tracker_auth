import time

import jwt

from auth_app.config import settings


def get_refresh_response(token: str) -> dict[str, str]:
    return {
        "refresh_token": token,
    }


def get_access_response(token: str) -> dict[str, str]:
    return {
        "access_token": token,
    }


def generate_refresh(user_id: str, email: str) -> dict[str, str]:
    payload = {
        "user_id": user_id,
        "email": email,
        "expires": time.time() + settings.REFRESH_LASTING,
        "token_type": "refresh",
    }
    token = jwt.encode(
        payload=payload,
        key=settings.KEY,
        algorithm=settings.ALGORITHM,
    )
    return get_refresh_response(token)


def generate_access(refresh_token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(
            jwt=refresh_token,
            key=settings.KEY,
            algorithm=settings.ALGORITHM,
        )

        token_type = payload.get("token_type")
        if token_type != "refresh":
            raise ValueError(f"Invalid token type: {token_type}")

        if payload.get("expires") < time.time():
            raise ValueError("Expired refresh token")

        access_payload = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "expires": time.time() + settings.ACCESS_LASTING,
            "token_type": "access",
        }
        access_token = jwt.encode(
            payload=access_payload,
            key=settings.KEY,
            algorithm=settings.ALGORITHM,
        )
        return get_access_response(access_token)
    except (jwt.ExpiredSignatureError, jwt.DecodeError, ValueError) as e:
        raise ValueError(f"Token update error: {e}") from e
