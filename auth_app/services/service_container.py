from collections.abc import AsyncGenerator

from aiobotocore.client import AioBaseClient
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.db.connect_db import get_db
from auth_app.db.connect_redis import get_redis_client
from auth_app.exeptions.custom import TransactionError
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.services.ses.clients import get_ses_client


# pylint: disable=too-many-instance-attributes
class ServiceContainer:
    """
    Dependencies initialization for the routers
    """

    def __init__(self) -> None:
        self.db_gen: AsyncGenerator[AsyncSession, None] | None = None
        self.pg_session: AsyncSession | None = None
        self.user_repo: UserRepo | None = None
        self.token_repo: TokenRepo | None = None
        self._transaction = None

        self.redis_gen: AsyncGenerator[Redis, None] | None = None
        self.redis: Redis | None = None

        self.ses_gen: AsyncGenerator[AioBaseClient, None] | None = None
        self.ses: AioBaseClient | None = None

    async def begin_transaction(self) -> None:
        session = await self.get_session()
        self._transaction = await session.begin()

    async def commit(self) -> None:
        if self._transaction:
            try:
                await self._transaction.commit()
            except Exception as e:
                raise TransactionError("Failed to commit transaction") from e
            finally:
                self._transaction = None

    async def rollback(self) -> None:
        if self._transaction:
            await self._transaction.rollback()
            self._transaction = None

    async def get_session(self) -> AsyncSession:
        if self.pg_session is None:
            self.db_gen = get_db()
            self.pg_session = await anext(self.db_gen)
        return self.pg_session

    async def get_user_repo(self) -> UserRepo:
        if self.user_repo is None:
            session = await self.get_session()
            self.user_repo = UserRepo(session)
        return self.user_repo

    async def get_token_repo(self) -> TokenRepo:
        if self.token_repo is None:
            session = await self.get_session()
            self.token_repo = TokenRepo(session)
        return self.token_repo

    async def get_redis(self) -> Redis:
        if self.redis is None:
            self.redis_gen = get_redis_client()
            self.redis = await anext(self.redis_gen)
        return self.redis

    async def get_ses(self) -> AioBaseClient:
        if self.ses is None:
            self.ses_gen = get_ses_client()
            self.ses = await anext(self.ses_gen)
        return self.ses

    async def close(self) -> None:
        await self.rollback()
        if self.db_gen is not None:
            await self.db_gen.aclose()

        if self.redis_gen is not None:
            await self.redis_gen.aclose()

        if self.ses_gen is not None:
            await self.ses_gen.aclose()


async def get_service_container() -> AsyncGenerator[ServiceContainer, None]:
    container = ServiceContainer()
    try:
        yield container
    finally:
        await container.close()
