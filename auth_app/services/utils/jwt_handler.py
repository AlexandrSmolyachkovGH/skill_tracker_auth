import time
from datetime import datetime

import jwt
from jwt import (
    DecodeError,
    InvalidSignatureError,
)

from auth_app.config import jwt_settings
from auth_app.exeptions.custom import TokenError
from auth_app.schemes.tokens import CreateDataScheme


class JWTHandler:
    """
    Service for implementing all basic JWT operations.
    Using the standard JWT library.
    """

    @staticmethod
    def get_refresh_response(
        token: str,
        payload: dict,
    ) -> dict:
        return {
            "refresh_token": token,
            "payload": payload,
        }

    @staticmethod
    def get_access_response(
        token: str,
    ) -> dict:
        return {
            "access_token": token,
        }

    def generate_refresh(
        self,
        create_data: CreateDataScheme,
    ) -> dict:
        secret = jwt_settings.ADMIN_SECRET.get_secret_value()
        if create_data.role != "USER" and create_data.admin_secret != secret:
            raise TokenError('Invalid admin secret')
        payload = {
            "user_id": create_data.user_id,
            "email": create_data.email,
            "role": create_data.role,
            "expires": time.time() + jwt_settings.REFRESH_LASTING,
            "token_type": "refresh",
        }
        token = jwt.encode(
            payload=payload,
            key=jwt_settings.KEY.get_secret_value(),
            algorithm=jwt_settings.ALGORITHM.get_secret_value(),
        )
        return self.get_refresh_response(token, payload)

    @staticmethod
    def base_decode(
        token: str,
    ) -> dict:
        try:
            payload = jwt.decode(
                jwt=token,
                key=jwt_settings.KEY.get_secret_value(),
                algorithms=[jwt_settings.ALGORITHM.get_secret_value()],
            )
            return payload

        except InvalidSignatureError as e:
            raise TokenError("Invalid Signature") from e
        except DecodeError as e:
            raise TokenError(f"{e}") from e

    def decode_token(
        self,
        token: str,
    ) -> dict:
        """
        Custom decoder with token expiration check.
        """
        payload = self.base_decode(token)

        if datetime.utcnow() > datetime.utcfromtimestamp(payload['expires']):
            raise TokenError('Expired token')
        return payload

    def generate_access(
        self,
        refresh_token: str,
        extra_payload: dict,
    ) -> dict[str, str]:
        payload = self.decode_token(token=refresh_token)
        token_type = payload.get("token_type")
        if token_type != "refresh":
            raise TokenError(f"Invalid token type: {token_type}")
        access_payload = {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "expires": time.time() + jwt_settings.ACCESS_LASTING,
            "token_type": "access",
        }
        access_payload.update(extra_payload)
        access_token = jwt.encode(
            payload=access_payload,
            key=jwt_settings.KEY.get_secret_value(),
            algorithm=jwt_settings.ALGORITHM.get_secret_value(),
        )
        return self.get_access_response(access_token)
