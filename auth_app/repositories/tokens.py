from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.schemas.tokens import (
    CreateRefresh,
    DeleteRefresh,
    GetRefresh,
)


class TokenRepo:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_token(self, create_data: CreateRefresh) -> GetRefresh | None:
        ...
