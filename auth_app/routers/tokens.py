from datetime import datetime
from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Security,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.config import settings
from auth_app.db.connect_db import get_db
from auth_app.repositories.tokens import TokenRepo
from auth_app.repositories.users import UserRepo
from auth_app.routers.users import get_repository as get_user_repo
from auth_app.schemes.tokens import (
    AuthData,
    CreateData,
    CreateRefresh,
    GetAccess,
    GetRefresh,
    UpdateRefresh,
)
from auth_app.schemes.users import RoleEnum
from auth_app.services.tokens.authenticate_user import authenticate_user
from auth_app.services.tokens.general import (
    requre_expired,
    verify_refresh,
)
from auth_app.services.tokens.jwt import (
    generate_access,
    generate_refresh,
)
from auth_app.services.tokens.security import oauth2_scheme

token_router = APIRouter(
    prefix='/tokens',
    tags=['tokens'],
)


# flake8: noqa: B008
async def get_repository(session: AsyncSession = Depends(get_db)) -> TokenRepo:
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
) -> Optional[GetRefresh]:
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
    status_code=status.HTTP_201_CREATED,
)
async def create_refresh(
    auth_data: Annotated[AuthData, Body()],
    role: str = RoleEnum.USER,
    admin_secret: Optional[str] = None,
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
    create_data = CreateData.model_validate(
        {
            "user_id": str(user.id),
            "email": user.email,
            "role": role,
            "admin_secret": admin_secret,
        }
    )
    token_data = generate_refresh(create_data)

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


@token_router.get(
    path='/refresh/exchange',
    response_model=GetRefresh,
    description='Generate new refresh token by using expired one',
    status_code=status.HTTP_201_CREATED,
)
async def exchange_refresh(
    token: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    repo: TokenRepo = Depends(get_repository),
) -> GetRefresh:
    token = token.credentials
    token, payload = requre_expired(token)
    is_user = payload.get("role") == "USER"
    admin_secret = (
        None if is_user else settings.ADMIN_SECRET.get_secret_value()
    )
    create_data = CreateData.model_validate(
        {
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "admin_secret": admin_secret,
        }
    )
    token_data = generate_refresh(create_data)
    new_token = token_data.get("refresh_token")
    new_payload = token_data.get("payload")
    if not isinstance(new_payload, dict):
        raise HTTPException(
            status_code=500,
            detail="Invalid payload format",
        )
    expires_at = new_payload["expires"]
    result = await repo.update_refresh(
        old_token=token,
        update_data=UpdateRefresh(
            token=new_token,
            expires_at=datetime.utcfromtimestamp(expires_at),
        ),
    )
    return result


@token_router.post(
    path='/access/create',
    response_model=GetAccess,
    description='Generate access token for the user',
    status_code=status.HTTP_201_CREATED,
)
async def create_access(
    token: HTTPAuthorizationCredentials = Security(oauth2_scheme),
) -> GetAccess:
    token = token.credentials
    token, _ = verify_refresh(token)
    try:
        result = generate_access(refresh_token=token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}"
        ) from e
    return GetAccess(message=result)
