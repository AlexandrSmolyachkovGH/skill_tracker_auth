from auth_app.config import jwt_settings
from auth_app.exeptions.custom import (
    ServiceError,
    UserVerificationError,
)
from auth_app.messages.common import msg_creator
from auth_app.models import UserORM
from auth_app.schemes.users import (
    CreateResponseScheme,
    CreateUserExtendedScheme,
    GetUserScheme,
    MessageResponseScheme,
    PatchUserScheme,
    RoleEnum,
)
from auth_app.services.service_container import ServiceContainer
from auth_app.services.ses.ses_handler import ses_handler
from auth_app.services.utils.pwd_hashing import hash_password
from auth_app.services.utils.verification import verify_auth_code


class UserService:
    @staticmethod
    async def create_user_record(
        user_data: CreateUserExtendedScheme,
        conn_container: ServiceContainer,
    ) -> UserORM:
        if user_data.role != RoleEnum.USER:
            if (
                user_data.admin_code
                != jwt_settings.ADMIN_SECRET.get_secret_value()
            ):
                raise ServiceError("Invalid role or permission code")
        user_repo = await conn_container.get_user_repo()
        record = await user_repo.create_user(user_data)
        return record

    @staticmethod
    async def create_init_code_message(
        record: UserORM,
        conn_container: ServiceContainer,
    ) -> CreateResponseScheme:
        ses = await conn_container.get_ses()
        redis_client = await conn_container.get_redis()
        email_to = record.email
        await ses_handler.send_confirmation_email(
            email_to=email_to,
            ses=ses,
            redis_client=redis_client,
        )
        response = {
            "record": GetUserScheme.model_validate(record),
            "message": msg_creator.get_code_message(email_to),
        }
        return CreateResponseScheme.model_validate(response)

    @staticmethod
    async def create_verification_code(
        payload: dict,
        conn_container: ServiceContainer,
    ) -> MessageResponseScheme:
        ses = await conn_container.get_ses()
        redis_client = await conn_container.get_redis()
        email_to = payload["email"]
        await ses_handler.send_confirmation_email(
            email_to=email_to,
            ses=ses,
            redis_client=redis_client,
        )
        response = {
            "message": msg_creator.get_code_message(email_to),
        }
        return MessageResponseScheme.model_validate(response)

    @staticmethod
    async def execute_verification(
        verification_code: str,
        payload: dict,
        conn_container: ServiceContainer,
    ) -> UserORM:
        repo = await conn_container.get_user_repo()
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
            user_id=payload["id"],
            patch_dict=patch_dict,
        )
        if not result:
            raise ServiceError("Record not found")
        return result

    @staticmethod
    async def reset_password(
        payload: dict,
        conn_container: ServiceContainer,
    ) -> dict:
        repo = await conn_container.get_user_repo()
        ses = await conn_container.get_ses()
        email_to = payload["email"]
        data = await ses_handler.reset_password(email_to=email_to, ses=ses)
        new_pwd_hash = hash_password(data["new_password"])
        patch_model = PatchUserScheme(password_hash=new_pwd_hash)
        patch_dict = patch_model.model_dump(
            exclude_unset=True,
            exclude_defaults=True,
        )
        record = await repo.update_user(
            user_id=payload["id"],
            patch_dict=patch_dict,
        )
        if not record:
            raise ServiceError("User not found or already deleted")
        response = {
            "message": data.get("message"),
        }
        return response


user_service = UserService()
