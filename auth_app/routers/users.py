from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    status,
)

from auth_app.schemes.users import (
    CreateResponseScheme,
    CreateUserExtendedScheme,
    GetUserScheme,
    MessageResponseScheme,
    UserFilterScheme,
)
from auth_app.services.service_container import (
    ServiceContainer,
    get_service_container,
)
from auth_app.services.users import user_service
from auth_app.services.utils.token_handler import (
    TokenData,
    get_current_token_payload,
    token_handler,
)

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@user_router.post(
    path="/",
    response_model=CreateResponseScheme,
    description="Create new user record",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: Annotated[CreateUserExtendedScheme, Body()],
    conn_container: ServiceContainer = Depends(get_service_container),
) -> CreateResponseScheme:
    await conn_container.begin_transaction()
    record = await user_service.create_user_record(
        user_data=user_data,
        conn_container=conn_container,
    )
    user = await user_service.create_init_code_message(
        record=record,
        conn_container=conn_container,
    )
    await conn_container.commit()
    return CreateResponseScheme.model_validate(user)


@user_router.get(
    path="/verification/get-code",
    response_model=MessageResponseScheme,
    description="Get verification code",
    status_code=status.HTTP_200_OK,
)
async def get_verification_code(
    token_data: TokenData = Depends(get_current_token_payload),
    conn_container: ServiceContainer = Depends(get_service_container),
) -> MessageResponseScheme:
    result = await user_service.create_verification_code(
        payload=token_data.payload,
        conn_container=conn_container,
    )
    return result


@user_router.patch(
    path="/verification/set-code",
    response_model=GetUserScheme,
    description="Verify the user record",
    status_code=status.HTTP_200_OK,
)
async def verify_record(
    verification_code: str,
    token_data: TokenData = Depends(get_current_token_payload),
    conn_container: ServiceContainer = Depends(get_service_container),
) -> GetUserScheme:
    await conn_container.begin_transaction()
    user = await user_service.execute_verification(
        verification_code=verification_code,
        payload=token_data.payload,
        conn_container=conn_container,
    )
    await conn_container.commit()
    return GetUserScheme.model_validate(user)


@user_router.patch(
    path='/reset-password',
    response_model=MessageResponseScheme,
    description='Verify the user record',
    status_code=status.HTTP_200_OK,
)
async def reset_pwd(
    token_data: TokenData = Depends(get_current_token_payload),
    conn_container: ServiceContainer = Depends(get_service_container),
) -> MessageResponseScheme:
    await conn_container.begin_transaction()
    result = await user_service.reset_password(
        payload=token_data.payload,
        conn_container=conn_container,
    )
    await conn_container.commit()
    return MessageResponseScheme.model_validate(result)


@user_router.get(
    path='/me',
    response_model=GetUserScheme,
    description="Retrieve the user by ID",
    status_code=status.HTTP_200_OK,
)
async def get_user(
    token_data: TokenData = Depends(get_current_token_payload),
    conn_container: ServiceContainer = Depends(get_service_container),
) -> GetUserScheme:
    user_repo = await conn_container.get_user_repo()
    user = await user_repo.get_user(token_data.payload["user_id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found or already deleted',
        )
    return GetUserScheme.model_validate(user)


@user_router.get(
    path='/',
    response_model=list[GetUserScheme],
    description="Get users",
    status_code=status.HTTP_200_OK,
)
async def get_users(
    filter_model: Annotated[UserFilterScheme, Query()],
    token_data: TokenData = Depends(get_current_token_payload),
    conn_container: ServiceContainer = Depends(get_service_container),
) -> list[GetUserScheme]:
    user_repo = await conn_container.get_user_repo()
    token_handler.verify_admin(token_data.token)
    filter_dict = filter_model.model_dump(
        exclude_unset=True,
    )
    users = await user_repo.get_users(
        filter_dict=filter_dict,
    )
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Relevant users not found',
        )
    return [GetUserScheme.model_validate(user) for user in users]
