from typing import Optional
from uuid import UUID

from sqlalchemy import insert, select, update

from auth_app.models.tokens import refresh_tokens
from auth_app.repositories.base import BaseRepo
from auth_app.schemes.tokens import (
    CreateRefresh,
    GetRefresh,
    UpdateRefresh,
)


class TokenRepo(BaseRepo):

    async def create_refresh(self, create_data: CreateRefresh) -> GetRefresh:
        data = create_data.model_dump()
        stmt = (
            insert(refresh_tokens).values(**data).returning(refresh_tokens.c)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        row = result.mappings().one()
        return GetRefresh.model_validate(row)

    async def get_refresh(self, user_id: UUID) -> Optional[GetRefresh]:
        stmt = select(refresh_tokens).where(
            refresh_tokens.c.user_id == user_id
        )
        result = await self.session.execute(stmt)
        row = result.mappings().first()
        return GetRefresh.model_validate(row) if row else None

    async def update_refresh(
        self, old_token: str, update_data: UpdateRefresh
    ) -> GetRefresh:
        data = update_data.model_dump()
        stmt = (
            update(refresh_tokens)
            .where(refresh_tokens.c.token == old_token)
            .values(**data)
            .returning(refresh_tokens.c)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        row = result.mappings().one()
        return GetRefresh.model_validate(row)
