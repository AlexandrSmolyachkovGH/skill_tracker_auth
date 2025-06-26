from aiobotocore.client import AioBaseClient
from fastapi import Depends
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.db.connect_redis import get_redis_client
from auth_app.middleware.db_session import get_db_from_request
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.services.ses.clients import get_ses_client
from auth_app.services.tokens import TokenService
from auth_app.services.users import UserService


async def get_user_service(
    session: AsyncSession = Depends(get_db_from_request),
    redis: Redis = Depends(get_redis_client),
    ses: AioBaseClient = Depends(get_ses_client),
) -> UserService:
    user_repo = UserRepo(session)
    token_repo = TokenRepo(session)
    return UserService(user_repo, token_repo, redis, ses)


async def get_token_service(
    session: AsyncSession = Depends(get_db_from_request),
    redis: Redis = Depends(get_redis_client),
    ses: AioBaseClient = Depends(get_ses_client),
) -> TokenService:
    user_repo = UserRepo(session)
    token_repo = TokenRepo(session)
    return TokenService(user_repo, token_repo, redis, ses)
