from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

token_router = APIRouter(
    prefix='/users',
    tags=['users'],
)


# flake8: noqa: B008
async def get_repository(
        session: AsyncSession = Depends()
) -> str | None:
    ...
