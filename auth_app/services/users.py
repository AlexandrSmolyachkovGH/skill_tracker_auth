from aiobotocore.client import AioBaseClient

from auth_app.config import jwt_settings
from auth_app.exeptions.custom import (
    ServiceError,
    UserVerificationError,
)
from auth_app.messages.common import msg_creator
from auth_app.models import UserORM
from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import (
    CreateResponseScheme,
    CreateUserExtendedScheme,
    GetUserScheme,
    MessageResponseScheme,
    PatchUserScheme,
    RoleEnum,
)
from auth_app.services.ses.pwd_reset import reset_password
from auth_app.services.ses.send_verification_code import (
    send_confirmation_email,
)
from auth_app.services.utils.pwd_hashing import hash_password
from auth_app.services.utils.verification import verify_auth_code


class UserService:
    @staticmethod
    async def create_user_record(
        user_data: CreateUserExtendedScheme,
        user_repo: UserRepo,
    ) -> UserORM:
        if user_data.role != RoleEnum.USER:
            if (
                user_data.admin_code
                != jwt_settings.ADMIN_SECRET.get_secret_value()
            ):
                raise ServiceError("Invalid role or permission code")
        record = await user_repo.create_user(user_data)
        return record

    @staticmethod
    async def create_init_code_message(
        record: UserORM,
        ses: AioBaseClient,
    ) -> CreateResponseScheme:
        email_to = record.email
        await send_confirmation_email(
            email_to=email_to,
            ses=ses,
        )
        response = {
            "record": GetUserScheme.model_validate(record),
            "message": msg_creator.get_code_message(email_to),
        }
        return CreateResponseScheme.model_validate(response)

    @staticmethod
    async def create_verification_code(
        payload: dict,
        ses: AioBaseClient,
    ) -> MessageResponseScheme:
        email_to = payload["email"]
        await send_confirmation_email(
            email_to=email_to,
            ses=ses,
        )
        response = {
            "message": msg_creator.get_code_message(email_to),
        }
        return MessageResponseScheme.model_validate(response)

    @staticmethod
    async def execute_verification(
        verification_code: str,
        payload: dict,
        repo: UserRepo,
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
        result = await repo.update_user(
            email=email_to,
            patch_dict=patch_dict,
        )
        if not result:
            raise ServiceError("Record not found")
        return result

    @staticmethod
    async def reset_password(
        payload: dict,
        repo: UserRepo,
        ses: AioBaseClient,
    ) -> dict:
        email_to = payload["email"]
        data = await reset_password(email_to=email_to, ses=ses)
        new_pwd_hash = hash_password(data["new_password"])
        patch_model = PatchUserScheme(password_hash=new_pwd_hash)
        patch_dict = patch_model.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
        )
        record = await repo.update_user(
            email=email_to,
            patch_dict=patch_dict,
        )
        if not record:
            raise ServiceError("User not found or already deleted")
        response = {
            "message": data.get("message"),
        }
        return response


user_service = UserService()
