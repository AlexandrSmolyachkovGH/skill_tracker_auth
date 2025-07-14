import random
from uuid import UUID

import httpx
from aiobotocore.client import AioBaseClient
from redis.asyncio.client import Redis

from auth_app.config import (
    core_service_settings,
    jwt_settings,
)
from auth_app.exeptions.custom import (
    ServiceError,
    UserActivityError,
    UserVerificationError,
)
from auth_app.messages.common import msg_creator
from auth_app.models import UserORM
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import (
    CreateResponseScheme,
    CreateUserExtendedScheme,
    DeleteUserScheme,
    GetUserScheme,
    MessageResponseScheme,
    PatchUserScheme,
    RoleEnum,
)
from auth_app.services.ses.ses_handler import ses_handler
from auth_app.services.utils.pwd_hashing import hash_password
from auth_app.services.utils.token_handler import TokenData


class UserService:
    def __init__(
        self,
        user_repo: UserRepo,
        token_repo: TokenRepo,
        redis: Redis,
        ses: AioBaseClient,
    ) -> None:
        self.__user_repo = user_repo
        self.__token_repo = token_repo  # pylint: disable=W0238
        self.__redis = redis
        self.__ses = ses

    @property
    def user_repo(self) -> UserRepo:
        return self.__user_repo

    @property
    def redis(self) -> Redis:
        return self.__redis

    @property
    def ses(self) -> AioBaseClient:
        return self.__ses

    async def verify_auth_code(
        self,
        email: str,
        code: str,
    ) -> bool:
        """
        Compare the transmitted one-time password with the cached one
        """
        cached_code = await self.__redis.get(f"otp:{email}")
        print(f"cached_code: {cached_code}, otp: {code}")
        return cached_code == code

    async def check_auth_statuses(
        self,
        user_data: GetUserScheme,
    ) -> None:
        if not user_data.is_verified:
            raise UserVerificationError()
        if not user_data.is_active:
            raise UserActivityError

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
        record = await self.__user_repo.create_user(user_data)
        try:
            await self.create_user_record_in_core(
                record=record,
            )
        except ServiceError as e:
            await self.__user_repo.delete_user(
                user_id=record.id,
            )
            raise ServiceError(
                f"Failed user creation on the core side: {e}"
            ) from e
        return record

    async def create_user_record_in_core(
        self,
        record: UserORM,
    ) -> None:
        headers = {
            "Service-Secret": f"{core_service_settings.SERVICE_SECRET.get_secret_value()}"
        }
        user_name = self.create_unique_username(record.email)
        user_data = {
            "id": str(record.id),
            "name": user_name,
            "email": record.email,
        }
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                core_service_settings.CREATE_USER_URI,
                headers=headers,
                json=user_data,
            )
        if response.status_code != 201:
            raise ServiceError(
                f"Core service rejected user: {response.text}"
            )

    async def create_init_code_message(
        self,
        record: UserORM,
    ) -> CreateResponseScheme:
        email_to = record.email
        await ses_handler.send_confirmation_email(
            email_to=email_to,
            ses=self.__ses,
            redis_client=self.__redis,
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
            ses=self.__ses,
            redis_client=self.__redis,
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
        check = await self.verify_auth_code(
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
        result = await self.__user_repo.update_user(
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
            ses=self.__ses,
        )
        new_pwd_hash = hash_password(data["new_password"])
        patch_model = PatchUserScheme(password_hash=new_pwd_hash)
        patch_dict = patch_model.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
        )
        record = await self.__user_repo.update_user(
            user_id=UUID(payload["user_id"]),
            patch_dict=patch_dict,
        )
        if not record:
            raise ServiceError("User not found or already deleted")
        response = {
            "message": data.get("message"),
        }
        return response

    def create_unique_username(
        self,
        email: str,
    ) -> str:
        username = email.split("@")[0]
        username = username + "_" + str(random.randint(100000, 999999))
        return username

    async def delete_user_record(
        self,
        token_data: TokenData,
        delete_model: DeleteUserScheme,
    ) -> UserORM:
        role = token_data.payload["role"]
        user_id = token_data.payload["user_id"]
        if delete_model.id is None:
            raise ServiceError("User ID must not be None")
        if role in ["USER"] and user_id != str(delete_model.id):
            raise ServiceError("Have no permissions to delete the record")
        record = await self.__user_repo.soft_delete_user(
            user_id=delete_model.id,
        )
        try:
            await self.delete_user_record_in_core(
                user_id=delete_model.id,
            )
        except ServiceError as e:
            await self.__user_repo.soft_delete_user_rollback(
                user_id=record.id,
            )
            raise ServiceError(
                f"Delete failure on the core side: {e}"
            ) from e
        return record

    async def delete_user_record_in_core(
        self,
        user_id: UUID,
    ) -> None:
        headers = {
            "Service-Secret": f"{core_service_settings.SERVICE_SECRET.get_secret_value()}"
        }
        uri = core_service_settings.DELETE_USER_URI + str(user_id) + "/"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.delete(
                uri,
                headers=headers,
            )
        if response.status_code != 200:
            raise ServiceError(
                f"Core service rejected delete operation: {response.text}"
            )
