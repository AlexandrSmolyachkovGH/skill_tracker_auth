from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.models.users import users
from auth_app.schemas.sign_up import (
    CreateUser,
    DeleteUser,
    GetUser,
    PatchUser,
    PutUser,
)


class UserSignUpRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, create_data: CreateUser) -> GetUser:
        stmt = insert(users).values(
            **create_data.model_dump()
        ).returning(*users.c)
        result = await self.session.execute(stmt)
        await self.session.commit()
        row = result.mappings().one()
        return GetUser.model_validate(row)

    async def get(self, user_id: int) -> GetUser | None:
        stmt = select(users).where(users.c.id == user_id)
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return GetUser.model_validate(row)

    # async def get_users(self, filter_dict: dict) -> list[GetUser]:
    #     stmt = select(users).where(...)
    #     result = await self.session.execute(stmt)
    #     rows = result.mappings().fetchall()
    #     return [GetUser.model_validate(prt) for prt in rows]
