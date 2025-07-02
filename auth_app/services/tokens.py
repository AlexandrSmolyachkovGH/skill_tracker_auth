from datetime import datetime

from aiobotocore.client import AioBaseClient
from redis.asyncio.client import Redis

from auth_app.config import jwt_settings
from auth_app.exeptions.custom import ServiceError
from auth_app.models import RefreshTokenORM
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.schemes.tokens import (
    CreateDataScheme,
    CreateRefreshScheme,
    RoleDataScheme,
    UpdateRefreshScheme,
)
from auth_app.schemes.users import AuthUserScheme
from auth_app.services.utils.authenticate_user import authenticate_user
from auth_app.services.utils.token_handler import (
    TokenData,
    token_handler,
)


class TokenService:
    def __init__(
        self,
        user_repo: UserRepo,
        token_repo: TokenRepo,
        redis: Redis,
        ses: AioBaseClient,
    ) -> None:
        self.__user_repo = user_repo
        self.__token_repo = token_repo
        self.__redis = redis  # pylint: disable=W0238
        self.__ses = ses  # pylint: disable=W0238

    @property
    def user_repo(self) -> UserRepo:
        return self.__user_repo

    @property
    def token_repo(self) -> TokenRepo:
        return self.__token_repo

    async def get_refresh_token(
        self,
        auth_data: AuthUserScheme,
    ) -> RefreshTokenORM:
        user = await authenticate_user(
            email=auth_data.email,
            password=auth_data.password_hash,
            user_repo=self.__user_repo,
        )
        if not user:
            raise ServiceError("User not found or Invalid user data")
        result = await self.__token_repo.get_refresh(
            user_id=user.id,
        )
        if not result:
            raise ServiceError("Token not found")
        return result

    async def create_refresh_token(
        self,
        auth_data: RoleDataScheme,
    ) -> RefreshTokenORM:
        user = await authenticate_user(
            email=auth_data.email,
            password=auth_data.password_hash,
            user_repo=self.__user_repo,
        )
        if not user:
            raise ServiceError('User not found or Invalid user data')
        token_exists = await self.__token_repo.get_refresh(user_id=user.id)
        if token_exists:
            raise ServiceError(
                'Token already exists. Get active token or exchange expired.'
            )
        create_data = CreateDataScheme(
            user_id=user.id,
            email=user.email,
            role=auth_data.role,
            admin_secret=auth_data.admin_secret,
        )
        token_data = token_handler.generate_refresh(create_data)
        payload = token_data["payload"]

        expires_raw = payload["expires"]
        if not isinstance(expires_raw, (float, int)):
            raise ValueError("expires must be a number")

        result = await self.__token_repo.create_refresh(
            create_data=CreateRefreshScheme(
                user_id=user.id,
                token=token_data.get('refresh_token'),
                expires_at=datetime.utcfromtimestamp(expires_raw),
            )
        )
        return result

    async def exchange_refresh_token(
        self,
        token_data: TokenData,
    ) -> RefreshTokenORM:
        token_data = token_handler.requre_expired(token_data.token)
        is_user = token_data.payload.get("role") == "USER"
        admin_secret = (
            None if is_user else jwt_settings.ADMIN_SECRET.get_secret_value()
        )
        create_data = CreateDataScheme(
            user_id=token_data.payload.get("user_id"),
            email=token_data.payload.get("email"),
            role=token_data.payload.get("role"),
            admin_secret=admin_secret,
        )
        new_token_data = token_handler.generate_refresh(create_data)
        new_token = new_token_data.get("refresh_token")
        new_payload = new_token_data.get("payload")
        if not isinstance(new_payload, dict):
            raise ServiceError("Invalid payload format")

        expires_at = new_payload["expires"]
        result = await self.__token_repo.update_refresh(
            old_token=token_data.token,
            update_data=UpdateRefreshScheme(
                token=new_token,
                expires_at=datetime.utcfromtimestamp(expires_at),
            ),
        )
        if not result:
            raise ServiceError("Token not found or already deleted")
        return result

    async def create_access_token(
        self,
        token_data: TokenData,
    ) -> dict[str, str]:
        token_data = token_handler.verify_refresh(token_data.token)
        user = await self.__user_repo.get_user(token_data.payload["user_id"])

        if not user or not user.is_verified or not user.is_active:
            raise ServiceError("User must be verified")

        extra_payload = {
            "is_verified": user.is_verified,
            "is_active": user.is_active,
        }
        access_token = token_handler.generate_access(
            refresh_token=token_data.token,
            extra_payload=extra_payload,
        )
        return access_token
