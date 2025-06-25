from uuid import UUID

from aiobotocore.client import AioBaseClient
from fastapi import Depends
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.config import jwt_settings
from auth_app.db.connect_redis import get_redis_client
from auth_app.exeptions.custom import (
    ServiceError,
    UserVerificationError,
)
from auth_app.messages.common import msg_creator
from auth_app.middleware.db_session import get_db_from_request
from auth_app.models import UserORM
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import (
    CreateResponseScheme,
    CreateUserExtendedScheme,
    GetUserScheme,
    MessageResponseScheme,
    PatchUserScheme,
    RoleEnum,
)
from auth_app.services.ses.clients import get_ses_client
from auth_app.services.ses.ses_handler import ses_handler
from auth_app.services.utils.pwd_hashing import hash_password
from auth_app.services.utils.verification import verify_auth_code


class UserService:
    def __init__(
        self,
        user_repo: UserRepo,
        token_repo: TokenRepo,
        redis: Redis,
        ses: AioBaseClient,
    ) -> None:
        self.__user_repo = user_repo
        self.__token_repo = token_repo
        self.__redis = redis
        self.__ses = ses

    @property
    def user_repo(self) -> UserRepo:
        return self.__user_repo

    @property
    def token_repo(self) -> TokenRepo:
        return self.__token_repo

    @property
    def redis(self) -> Redis:
        return self.__redis

    @property
    def ses(self) -> AioBaseClient:
        return self.__ses

    async def create_user_record(
        self,
        user_data: CreateUserExtendedScheme,
    ) -> UserORM:
        if user_data.role != RoleEnum.USER:
            if (
                user_data.admin_code
                != jwt_settings.ADMIN_SECRET.get_secret_value()
            ):
                raise ServiceError("Invalid role or permission code")
        record = await self.user_repo.create_user(user_data)
        return record

    async def create_init_code_message(
        self,
        record: UserORM,
    ) -> CreateResponseScheme:
        email_to = record.email
        await ses_handler.send_confirmation_email(
            email_to=email_to,
            ses=self.ses,
            redis_client=self.redis,
        )
        response = {
            "record": GetUserScheme.model_validate(record),
            "message": msg_creator.get_code_message(email_to),
        }
        return CreateResponseScheme.model_validate(response)

    async def create_verification_code(
        self,
        payload: dict,
    ) -> MessageResponseScheme:
        email_to = payload["email"]
        await ses_handler.send_confirmation_email(
            email_to=email_to,
            ses=self.ses,
            redis_client=self.redis,
        )
        response = {
            "message": msg_creator.get_code_message(email_to),
        }
        return MessageResponseScheme.model_validate(response)

    async def execute_verification(
        self,
        verification_code: str,
        payload: dict,
    ) -> UserORM:
        email_to = payload["email"]
        check = await verify_auth_code(
            email=email_to,
            code=verification_code,
        )
        if not check:
            raise UserVerificationError()
        patch_model = PatchUserScheme(is_verified=True)
        patch_dict = patch_model.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
        )
        result = await self.user_repo.update_user(
            user_id=UUID(payload["user_id"]),
            patch_dict=patch_dict,
        )
        if not result:
            raise ServiceError("Record not found")
        return result

    async def reset_password(
        self,
        payload: dict,
    ) -> dict:
        email_to = payload["email"]
        data = await ses_handler.reset_password(
            email_to=email_to,
            ses=self.ses,
        )
        new_pwd_hash = hash_password(data["new_password"])
        patch_model = PatchUserScheme(password_hash=new_pwd_hash)
        patch_dict = patch_model.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
        )
        record = await self.user_repo.update_user(
            user_id=UUID(payload["user_id"]),
            patch_dict=patch_dict,
        )
        if not record:
            raise ServiceError("User not found or already deleted")
        response = {
            "message": data.get("message"),
        }
        return response


async def get_user_service(
    session: AsyncSession = Depends(get_db_from_request),
    redis: Redis = Depends(get_redis_client),
    ses: AioBaseClient = Depends(get_ses_client),
) -> UserService:
    user_repo = UserRepo(session)
    token_repo = TokenRepo(session)
    return UserService(user_repo, token_repo, redis, ses)
