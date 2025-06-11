from uuid import UUID

from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.models.tokens import refresh_tokens
from auth_app.schemes.tokens import (
    CreateRefresh,
    DeleteRefresh,
    GetRefresh,
)


class TokenRepo:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh(self, create_data: CreateRefresh) -> GetRefresh:
        data = create_data.model_dump()
        stmt = (
            insert(refresh_tokens)
            .values(**data)
            .returning(refresh_tokens.c)
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return GetRefresh.model_validate(row)

    async def get_refresh(self, user_id: UUID) -> GetRefresh:
        stmt = (
            select(refresh_tokens)
            .where(refresh_tokens.c.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return GetRefresh.model_validate(row)
