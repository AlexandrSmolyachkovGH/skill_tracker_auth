from typing import Annotated, Optional

from aiobotocore.client import AioBaseClient
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Security,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from auth_app.db.connect_db import get_db
from auth_app.repositories.users import UserRepo
from auth_app.schemes.users import (
    CreateResponse,
    CreateUser,
    GetUser,
    MessageResponse,
    PatchUser,
    UserFilter,
)
from auth_app.services.aws.ses.clients import get_ses_client
from auth_app.services.aws.ses.pwd_reset import reset_password
from auth_app.services.aws.ses.send_otp_email import send_confirmation_email
from auth_app.services.tokens.general import (
    verify_admin,
    verify_refresh,
)
from auth_app.services.tokens.security import oauth2_scheme
from auth_app.services.users.verification import verify_otp
from auth_app.services.utils.pwd_hashing import hash_password

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# flake8: noqa: B008
async def get_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepo:
    return UserRepo(session)


@user_router.post(
    path="/",
    response_model=CreateResponse,
    description="Create new user record",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: CreateUser,
    user_repo: UserRepo = Depends(get_repository),
    ses: AioBaseClient = Depends(get_ses_client),
) -> CreateResponse:
    record = await user_repo.create_user(user_data)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Creation error. Check the data and try again.",
        )
    email_to = record.model_dump().get("email")
    await send_confirmation_email(
        email_to=email_to,
        ses=ses,
    )
    response = {
        "record": record,
        "message": f"Verification code was sent to email: {email_to}",
    }
    return CreateResponse.model_validate(response)


@user_router.get(
    path="/verification/get-code",
    response_model=MessageResponse,
    description="Get verification code",
    status_code=status.HTTP_200_OK,
)
async def get_otp(
    token: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    ses: AioBaseClient = Depends(get_ses_client),
) -> MessageResponse:
    token = token.credentials
    token, payload = verify_refresh(token)
    await send_confirmation_email(
        email_to=payload["email"],
        ses=ses,
    )
    response = {
        "message": f"Your OTP-code was sent to {payload['email']}",
    }
    return MessageResponse.model_validate(response)


@user_router.patch(
    path="/verification/set-code",
    response_model=GetUser,
    description="Verify the user record",
    status_code=status.HTTP_200_OK,
)
async def verify_record(
    verification_code: str,
    token: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    user_repo: UserRepo = Depends(get_repository),
) -> Optional[GetUser]:
    token = token.credentials
    token, payload = verify_refresh(token)
    check = await verify_otp(
        email=payload["email"],
        code=verification_code,
    )
    if not check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid or expired data',
        )
    patch_model = PatchUser.model_validate({'is_verified': True})
    patch_dict = patch_model.model_dump(exclude_unset=True, exclude_none=True)
    result = await user_repo.patch_user(
        email=payload["email"],
        patch_dict=patch_dict,
    )
    return result


@user_router.patch(
    path='/reset-password',
    response_model=MessageResponse,
    description='Verify the user record',
    status_code=status.HTTP_200_OK,
)
async def reset_pwd(
    token: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    user_repo: UserRepo = Depends(get_repository),
    ses: AioBaseClient = Depends(get_ses_client),
) -> MessageResponse:
    token = token.credentials
    token, payload = verify_refresh(token)
    data = await reset_password(email_to=payload["email"], ses=ses)
    new_pwd_hash = hash_password(data["new_password"])
    patch_model = PatchUser.model_validate({"password_hash": new_pwd_hash})
    patch_dict = patch_model.model_dump(exclude_unset=True, exclude_none=True)
    await user_repo.patch_user(
        email=payload["email"],
        patch_dict=patch_dict,
    )
    response = {
        "message": data.get("message"),
    }
    return MessageResponse.model_validate(response)


@user_router.get(
    path='/me',
    response_model=GetUser,
    description="Retrieve the user by ID",
    status_code=status.HTTP_200_OK,
)
async def get_user(
    token: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    user_repo: UserRepo = Depends(get_repository),
) -> GetUser:
    token = token.credentials
    token, payload = verify_refresh(token)
    record = await user_repo.get_user(payload["email"])
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
    token: HTTPAuthorizationCredentials = Security(oauth2_scheme),
    user_repo: UserRepo = Depends(get_repository),
) -> list[GetUser]:
    token = token.credentials
    verify_admin(token)
    filter_dict = filter_model.model_dump(
        exclude_unset=True, exclude_none=True
    )
    records = await user_repo.get_users(filter_dict=filter_dict)
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Users not found',
        )
    return records
