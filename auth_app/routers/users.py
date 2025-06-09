from uuid import UUID

from aiobotocore.client import AioBaseClient
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.db.connect_db import get_db
from auth_app.repositories.users import UserRepo
from auth_app.schemas.users import (
    CreateUser,
    GetUser,
    UserFilter,
)
from auth_app.services.aws.clients import get_ses_client
from auth_app.services.aws.send_otp_email import send_confirmation_email

user_router = APIRouter(
    prefix='/users',
    tags=['users'],
)


# flake8: noqa: B008
async def get_repository(
        session: AsyncSession = Depends(get_db)
) -> UserRepo:
    return UserRepo(session)


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
    description="Retrieve a list of users",
    status_code=status.HTTP_200_OK,
)
async def get_users(
        filter_model: UserFilter = Depends(),
        user_repo: UserRepo = Depends(get_repository),
) -> list[GetUser]:
    records = await user_repo.get_users(filter_dict=filter_model.model_dump())
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Users not found',
        )
    return records


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
