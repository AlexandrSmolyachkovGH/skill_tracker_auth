from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.db.connect_db import get_db
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.routers.users import get_repository as get_user_repo
from auth_app.schemes.tokens import (
    GetAccessScheme,
    GetRefreshScheme,
    RoleDataScheme,
)
from auth_app.schemes.users import (
    AuthUserScheme,
)
from auth_app.services.tokens import token_service
from auth_app.services.utils.token_handler import (
    TokenData,
    get_current_token_payload,
)

token_router = APIRouter(
    prefix='/tokens',
    tags=['tokens'],
)


# flake8: noqa: B008
async def get_repository(session: AsyncSession = Depends(get_db)) -> TokenRepo:
    return TokenRepo(session)


@token_router.post(
    path='/refresh/get',
    response_model=GetRefreshScheme,
    description='Get refresh token for the user',
    status_code=status.HTTP_200_OK,
)
async def get_refresh(
    auth_data: Annotated[AuthUserScheme, Body()],
    repo: TokenRepo = Depends(get_repository),
    user_repo: UserRepo = Depends(get_user_repo),
) -> GetRefreshScheme:
    token = await token_service.get_refresh_token(
        auth_data=auth_data,
        repo=repo,
        user_repo=user_repo,
    )
    return GetRefreshScheme.model_validate(token)


@token_router.post(
    path='/refresh/create',
    response_model=GetRefreshScheme,
    description='Generate refresh token for the user',
    status_code=status.HTTP_201_CREATED,
)
async def create_refresh(
    auth_data: Annotated[RoleDataScheme, Body()],
    repo: TokenRepo = Depends(get_repository),
    user_repo: UserRepo = Depends(get_user_repo),
) -> GetRefreshScheme:
    try:
        token = await token_service.create_refresh_token(
            auth_data=auth_data,
            repo=repo,
            user_repo=user_repo,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}"
        ) from e
    return GetRefreshScheme.model_validate(token)


@token_router.get(
    path='/refresh/exchange',
    response_model=GetRefreshScheme,
    description='Generate new refresh token by using expired one',
    status_code=status.HTTP_201_CREATED,
)
async def exchange_refresh(
    token_data: TokenData = Depends(get_current_token_payload),
    repo: TokenRepo = Depends(get_repository),
) -> GetRefreshScheme:
    token = await token_service.exchange_refresh_token(
        token_data=token_data,
        repo=repo,
    )
    return GetRefreshScheme.model_validate(token)


@token_router.post(
    path='/access/create',
    response_model=GetAccessScheme,
    description='Generate access token for the user',
    status_code=status.HTTP_201_CREATED,
)
async def create_access(
    token_data: TokenData = Depends(get_current_token_payload),
    user_repo: UserRepo = Depends(get_user_repo),
) -> GetAccessScheme:
    token = await token_service.create_access_token(
        token_data=token_data,
        user_repo=user_repo,
    )
    return GetAccessScheme(message=token)
