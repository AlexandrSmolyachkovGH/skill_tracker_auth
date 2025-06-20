from sqlalchemy import (
    and_,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert

from auth_app.models.users import UserORM
from auth_app.repositories.base import BaseRepo
from auth_app.schemes.users import (
    CreateUserExtendedScheme,
)
from auth_app.services.utils.pwd_hashing import (
    hash_password,
)


class UserRepo(BaseRepo):

    async def create_user(
        self,
        create_data: CreateUserExtendedScheme,
    ) -> UserORM:
        try:
            data = create_data.model_dump()
            data.pop("admin_code", None)
            data['password_hash'] = hash_password(data.get('password_hash'))
            stmt = pg_insert(UserORM).values(**data).returning(UserORM)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.scalar_one()
        except Exception as e:
            await self.session.rollback()
            print("Ошибка при создании пользователя:", e)
            raise

    async def get_user(
        self,
        email: str,
    ) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_users(
        self,
        filter_dict: dict | None,
    ) -> list[UserORM]:
        stmt = select(UserORM)
        conditions = []
        if not filter_dict:
            filter_dict = {}
        for k, v in filter_dict.items():
            column = getattr(UserORM, k, None)
            if column is not None:
                conditions.append(column == v)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_user(
        self,
        email: str,
        patch_dict: dict,
    ) -> UserORM | None:
        stmt = (
            update(UserORM)
            .where(UserORM.email == email)
            .values(**patch_dict)
            .returning(UserORM)
        )
        row = await self.session.execute(stmt)
        await self.session.commit()
        result = row.scalars().first()
        return result
