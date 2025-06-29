from typing import Optional

from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import GetUserScheme
from auth_app.services.utils.pwd_hashing import verify_password


async def authenticate_user(
    email: str,
    password: str,
    user_repo: UserRepo,
) -> Optional[GetUserScheme]:
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
    return user
