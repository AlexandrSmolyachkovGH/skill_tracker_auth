from typing import Optional
from uuid import UUID

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.models.users import users
from auth_app.schemes.users import (
    CreateUser,
    GetUser,
)
from auth_app.services.fields.users import UserFields
from auth_app.services.utils.pwd_hashing import (
    hash_password,
)


class UserRepo:
    fields = UserFields

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, create_data: CreateUser) -> GetUser:
        data = create_data.model_dump()
        data['password_hash'] = hash_password(data.get('password_hash'))
        stmt = (
            insert(users)
            .values(**data)
            .returning(*users.c)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        row = result.mappings().one()
        return GetUser.model_validate(row)

    async def get_user(self, user_id: UUID) -> GetUser:
        stmt = (
            select(users)
            .where(users.c.id == user_id)
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return GetUser.model_validate(row)

    async def get_users(self, filter_dict: Optional[dict]) -> list[GetUser]:
        stmt = select(users)
        conditions = []
        if not filter_dict:
            filter_dict = {}
        for k, v in filter_dict.items():
            column = getattr(users.c, k, None)
            if column is not None:
                conditions.append(column == v)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self.session.execute(stmt)
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
        await self.session.commit()
        row = result.mappings().one()
        return GetUser.model_validate(row)

    async def patch_user(self, email: str, patch_dict: dict) -> GetUser:
        stmt = (
            update(users)
            .where(users.c.email == email)
            .values(**patch_dict)
            .returning(*users.c)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
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
