from auth_app.db.connect_redis import redis_client
from auth_app.exeptions.custom import (
    UserActivityError,
    UserVerificationError,
)
from auth_app.schemes.users import GetUser


async def verify_otp(email: str, code: str) -> bool:
    """
    Compare the transmitted one-time password with the cached one
    """
    cached_code = await redis_client.get(f"otp:{email}")
    print(f"cached_code: {cached_code}, otp: {code}")
    return cached_code == code


async def check_auth_statuses(user_data: GetUser) -> None:
    if not user_data.is_verified:
        raise UserVerificationError()
    if not user_data.is_active:
        raise UserActivityError
