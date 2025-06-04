from typing import Optional
from uuid import UUID

from sqlalchemy import delete, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.models.users import users
from auth_app.schemas.users import (
    CreateUser,
    GetUser,
)
from auth_app.services.fields.users import UserFields


class UserRepo:
    fields = UserFields

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, create_data: CreateUser) -> GetUser:
        stmt = (
            insert(users)
            .values(**create_data.model_dump())
            .returning(*users.c)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        row = result.mappings().one()
        return GetUser.model_validate(row)

    async def get_user(self, user_id: UUID) -> GetUser | None:
        stmt = (
            select(users)
            .where(users.c.id == user_id)
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return GetUser.model_validate(row)

    async def get_users(self, filter_dict: Optional[dict]) -> list[GetUser]:
        base_sql = f"""
        SELECT {self.fields.get_fields_str()}
        FROM users
        """
        if filter_dict:
            where_clause = " AND ".join(
                [f"users.{key} = :{key}" for key in filter_dict.keys()]
            )
            base_sql += where_clause
        stmt = text(base_sql)
        result = await self.session.execute(stmt, filter_dict or {})
        rows = result.mappings().fetchall()
        return [GetUser.model_validate(prt) for prt in rows]

    async def put_user(self, user_id: UUID, put_dict: dict) -> GetUser:
        stmt = (
            update(users)
            .where(users.c.id == user_id)
            .values(**put_dict)
            .returning(*users.c)
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return GetUser.model_validate(row)

    async def delete_user(self, user_id: UUID) -> GetUser:
        stmt = (
            delete(users)
            .where(users.c.id == user_id)
            .returning(*users.c)
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return GetUser.model_validate(row)
