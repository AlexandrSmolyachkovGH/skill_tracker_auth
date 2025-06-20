from uuid import UUID

from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert

from auth_app.models.tokens import RefreshTokenORM
from auth_app.repositories.base import BaseRepo
from auth_app.schemes.tokens import (
    CreateRefreshScheme,
    UpdateRefreshScheme,
)


class TokenRepo(BaseRepo):

    async def create_refresh(
        self,
        create_data: CreateRefreshScheme,
    ) -> RefreshTokenORM:
        stmt = (
            pg_insert(RefreshTokenORM)
            .values(**create_data.model_dump())
            .returning(RefreshTokenORM)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_refresh(
        self,
        user_id: UUID,
    ) -> RefreshTokenORM | None:
        stmt = select(RefreshTokenORM).where(
            RefreshTokenORM.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_refresh(
        self,
        old_token: str,
        update_data: UpdateRefreshScheme,
    ) -> RefreshTokenORM | None:
        stmt = (
            update(RefreshTokenORM)
            .where(RefreshTokenORM.token == old_token)
            .values(**update_data.model_dump())
            .returning(RefreshTokenORM)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
