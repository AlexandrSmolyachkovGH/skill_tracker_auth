from datetime import datetime
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.db.connect_db import get_db
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.routers.users import get_repository as get_user_repo
from auth_app.schemes.tokens import (
    AuthData,
    CreateRefresh,
    GetRefresh,
)
from auth_app.services.tokens.authenticate_user import authenticate_user
from auth_app.services.tokens.jwt import generate_refresh

token_router = APIRouter(
    prefix='/tokens',
    tags=['tokens'],
)


# flake8: noqa: B008
async def get_repository(
        session: AsyncSession = Depends(get_db)
) -> TokenRepo:
    return TokenRepo(session)


@token_router.post(
    path='/refresh/get',
    response_model=GetRefresh,
    description='Get refresh token for the user',
    status_code=status.HTTP_200_OK,
)
async def get_refresh(
        auth_data: Annotated[AuthData, Body()],
        repo: TokenRepo = Depends(get_repository),
        user_repo: UserRepo = Depends(get_user_repo),
) -> GetRefresh:
    user = await authenticate_user(
        **auth_data.model_dump(),
        user_repo=user_repo,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found or Invalid user data',
        )
    result = await repo.get_refresh(
        user_id=user.id,
    )
    return result


@token_router.post(
    path='/refresh/create',
    response_model=GetRefresh,
    description='Generate refresh token for the user',
    status_code=status.HTTP_201_CREATED
)
async def create_refresh(
        auth_data: Annotated[AuthData, Body()],
        repo: TokenRepo = Depends(get_repository),
        user_repo: UserRepo = Depends(get_user_repo),
) -> GetRefresh:
    user = await authenticate_user(
        **auth_data.model_dump(),
        user_repo=user_repo,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found or Invalid user data',
        )
    token_data = generate_refresh(
        user_id=str(user.id),
        email=user.email,
    )
    payload = token_data.get("payload")
    if not isinstance(payload, dict):
        raise ValueError()
    expires_raw = payload.get("expires")
    if not isinstance(expires_raw, (float, int)):
        raise ValueError("expires must be a number")
    result = await repo.create_refresh(
        create_data=CreateRefresh(
            user_id=user.id,
            token=token_data.get('refresh_token'),
            expires_at=datetime.utcfromtimestamp(expires_raw),
        )
    )
    return result
