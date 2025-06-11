from typing import Annotated
from uuid import UUID

from aiobotocore.client import AioBaseClient
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
from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import (
    AuthUserData,
    CreateUser,
    GetUser,
    PatchUser,
    UserFilter,
    VerificationData,
)
from auth_app.services.aws.clients import get_ses_client
from auth_app.services.aws.pwd_reset import reset_password
from auth_app.services.aws.send_otp_email import send_confirmation_email
from auth_app.services.users.verification import verify_otp
from auth_app.services.utils.pwd_hashing import hash_password

user_router = APIRouter(
    prefix='/users',
    tags=['users'],
)


# flake8: noqa: B008
async def get_repository(
        session: AsyncSession = Depends(get_db)
) -> UserRepo:
    return UserRepo(session)


@user_router.post(
    path='/',
    response_model=GetUser,
    description='Create new user record',
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
        user_data: CreateUser,
        user_repo: UserRepo = Depends(get_repository),
        ses: AioBaseClient = Depends(get_ses_client)

) -> GetUser:
    record = await user_repo.create_user(user_data)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creation error"
        )
    email_to = record.model_dump().get('email')
    await send_confirmation_email(
        email_to=email_to,
        ses=ses,
    )
    return record


@user_router.post(
    path='/verification/get-code',
    description="Get verification code",
    status_code=status.HTTP_200_OK,
)
async def get_otp(
        data: Annotated[AuthUserData, Body()],
        ses: AioBaseClient = Depends(get_ses_client)
) -> dict:
    # pass check

    await send_confirmation_email(
        email_to=data.email,
        ses=ses,
    )
    return {
        'message': f'Your OTP-code was sent to {data.email}',
        'status': status.HTTP_200_OK,
    }


@user_router.patch(
    path='/verification/set-code',
    response_model=GetUser,
    description='Verify the user record',
    status_code=status.HTTP_200_OK,
)
async def verify_record(
        data: Annotated[VerificationData, Body()],
        user_repo: UserRepo = Depends(get_repository),
) -> GetUser:
    check = await verify_otp(
        email=data.email,
        code=data.verification_code,
    )
    if not check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired data'
        )
    patch_model = PatchUser.model_validate({'is_verified': True})
    patch_dict = patch_model.model_dump(exclude_unset=True, exclude_none=True)
    result = await user_repo.patch_user(
        email=data.email,
        patch_dict=patch_dict,
    )
    return result


@user_router.patch(
    path='/reset-password',
    description='Verify the user record',
    status_code=status.HTTP_200_OK,
)
async def reset_pwd(
        email: Annotated[str, Query()],
        user_repo: UserRepo = Depends(get_repository),
        ses: AioBaseClient = Depends(get_ses_client),
) -> dict:
    new_pwd = await reset_password(email_to=email, ses=ses)
    new_pwd_hash = hash_password(new_pwd)
    patch_model = PatchUser.model_validate({'password_hash': new_pwd_hash})
    patch_dict = patch_model.model_dump(exclude_unset=True, exclude_none=True)
    await user_repo.patch_user(
        email=email,
        patch_dict=patch_dict,
    )
    return {
        'message': f'Your password was changed and sent to email: {email}',
        'status': status.HTTP_200_OK,
    }


@user_router.get(
    path='/{user_id}',
    response_model=GetUser,
    description="Retrieve the user by ID",
    status_code=status.HTTP_200_OK,
)
async def get_user(
        user_id: UUID = Path(description="Filter by user ID"),
        user_repo: UserRepo = Depends(get_repository),
) -> GetUser:
    record = await user_repo.get_user(user_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )
    return record


@user_router.get(
    path='/',
    response_model=list[GetUser],
    description="Get users",
    status_code=status.HTTP_200_OK,
)
async def get_users(
        filter_model: Annotated[UserFilter, Query()],
        user_repo: UserRepo = Depends(get_repository),

) -> list[GetUser]:
    filter_dict = filter_model.model_dump(exclude_unset=True, exclude_none=True)
    records = await user_repo.get_users(filter_dict=filter_dict)
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Users not found',
        )
    return records
