from typing import cast

from sqlalchemy import (
    select,
    update,
)

from auth_app.models.users import UserORM
from auth_app.repositories.base import BaseRepo
from auth_app.schemes.users import (
    CreateUserExtendedScheme,
)
from auth_app.services.utils.pwd_hashing import (
    hash_password,
)


class UserRepo(BaseRepo):
    @staticmethod
    def _build_filter_condition(
        filter_dict: dict,
    ) -> list:
        conditions = []
        for k, v in filter_dict.items():
            column = getattr(UserORM, k, None)
            conditions.append(column == v)
        return conditions

    async def create_user(
        self,
        create_data: CreateUserExtendedScheme,
    ) -> UserORM:

        data = create_data.model_dump()
        data.pop("admin_code", None)
        data['password_hash'] = hash_password(data.get('password_hash'))
        orm_data = UserORM(**data)

        self.session.add(orm_data)
        await self.session.flush()
        await self.session.refresh(orm_data)

        return orm_data

    async def get_user(
        self,
        user_id: str,
    ) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_users(
        self,
        filter_dict: dict | None,
    ) -> list[UserORM]:
        stmt = select(UserORM)
        filter_dict = filter_dict or {}
        conditions = self._build_filter_condition(filter_dict=filter_dict)
        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.session.execute(stmt)
        return cast(list, result.scalars().all())

    async def update_user(
        self,
        user_id: str,
        patch_dict: dict,
    ) -> UserORM | None:
        stmt = (
            update(UserORM)
            .where(UserORM.id == user_id)
            .values(**patch_dict)
            .returning(UserORM)
        )

        row = await self.session.execute(stmt)
        result = row.scalars().first()
        return result
