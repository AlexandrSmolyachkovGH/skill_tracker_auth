from typing import Optional

from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import GetUser
from auth_app.services.users.verification import check_auth_statuses
from auth_app.services.utils.pwd_hashing import verify_password


async def authenticate_user(
        email: str,
        password: str,
        user_repo: UserRepo,
) -> Optional[GetUser]:
    users = await user_repo.get_users(
        {
            'email': email,
        }
    )
    user = users[0] if users else None
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    await check_auth_statuses(user_data=user)
    return user
