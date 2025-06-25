from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)

from auth_app.schemes.tokens import (
    GetAccessScheme,
    GetRefreshScheme,
    RoleDataScheme,
)
from auth_app.schemes.users import (
    AuthUserScheme,
)
from auth_app.services.tokens import (
    TokenService,
    get_token_service,
)
from auth_app.services.utils.token_handler import (
    TokenData,
    get_current_token_payload,
)

token_router = APIRouter(
    prefix='/tokens',
    tags=['tokens'],
)


@token_router.post(
    path='/refresh/get',
    response_model=GetRefreshScheme,
    description='Get refresh token for the user',
    status_code=status.HTTP_200_OK,
)
async def get_refresh(
    auth_data: Annotated[AuthUserScheme, Body()],
    token_service: TokenService = Depends(get_token_service),
) -> GetRefreshScheme:
    token = await token_service.get_refresh_token(
        auth_data=auth_data,
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
    token_service: TokenService = Depends(get_token_service),
) -> GetRefreshScheme:
    try:
        token = await token_service.create_refresh_token(
            auth_data=auth_data,
        )
    except Exception as e:
        print(f"[DEBUG] Token creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}"
        ) from e
    return GetRefreshScheme.model_validate(token, from_attributes=True)


@token_router.get(
    path='/refresh/exchange',
    response_model=GetRefreshScheme,
    description='Generate new refresh token by using expired one',
    status_code=status.HTTP_201_CREATED,
)
async def exchange_refresh(
    token_data: TokenData = Depends(get_current_token_payload),
    token_service: TokenService = Depends(get_token_service),
) -> GetRefreshScheme:
    token = await token_service.exchange_refresh_token(
        token_data=token_data,
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
    token_service: TokenService = Depends(get_token_service),
) -> GetAccessScheme:
    token = await token_service.create_access_token(
        token_data=token_data,
    )
    return GetAccessScheme(message=token)
