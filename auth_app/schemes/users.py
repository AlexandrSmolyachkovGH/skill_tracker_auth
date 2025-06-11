from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    STAFFER = 'STAFFER'
    OTHER = 'OTHER'


client_roles = [
    RoleEnum.USER,
]
stuffer_roles = [
    RoleEnum.ADMIN,
    RoleEnum.STAFFER,
    RoleEnum.OTHER,
]


class AuthUserData(BaseModel):
    email: EmailStr = Field(
        description='Unique email address',
        example='joe.0101@example.com',
    )
    password_hash: str = Field(
        description='Password of the user',
        example='MySecurePassword123!',
        min_length=6,
        max_length=100,
    )


class CreateUser(AuthUserData):
    role: Optional[RoleEnum] = Field(
        description="User role in ['USER', 'ADMIN'] and etc",
        example='USER',
        default=RoleEnum.USER,
    )


class GetUser(AuthUserData):
    id: UUID = Field(
        description='Unique user identifier',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    role: RoleEnum = Field(
        description="User role in ['USER', 'ADMIN'] and etc",
        example='USER',
        default=RoleEnum.USER,
    )
    is_verified: bool = Field(
        description="Verification status",
        example=True,
        default=False,
    )
    is_active: bool = Field(
        description="Activity status",
        example=True,
        default=True,
    )


class PatchUser(BaseModel):
    email: Optional[EmailStr] = Field(
        description='Unique email address',
        example='joe.0101@example.com',
        default=None,
    )
    password_hash: Optional[str] = Field(
        description='Password of the user',
        example='MySecurePassword123!',
        min_length=6,
        max_length=100,
        default=None,
    )
    is_verified: Optional[bool] = Field(
        description="Verification status",
        example=True,
        default=False,
    )
    is_active: Optional[bool] = Field(
        description="Activity status",
        example=True,
        default=True,
    )


class PutUser(AuthUserData):
    is_verified: bool = Field(
        description="Verification status",
        example=True,
        default=False,
    )
    is_active: bool = Field(
        description="Activity status",
        example=True,
        default=True,
    )


class DeleteUser(AuthUserData):
    id: Optional[UUID] = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
        default=None,
    )


class UserFilter(BaseModel):
    id: Optional[UUID] = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
        default=None,
    )
    email: Optional[EmailStr] = Field(
        description='Unique email address',
        example='joe.0101@example.com',
        default=None,
    )
    role: Optional[RoleEnum] = Field(
        description="User role in ['USER', 'ADMIN'] and etc",
        example='USER',
        default=None,
    )
    is_verified: Optional[bool] = Field(
        description="Verification status",
        example=True,
        default=None,
    )
    is_active: Optional[bool] = Field(
        description="Activity status",
        example=True,
        default=None,
    )


class VerificationData(BaseModel):
    email: EmailStr = Field(
        description='Unique email address',
        example='joe.0101@example.com',
    )
    verification_code: str = Field(
        description='Valid OTP-code received via email',
        example='123e4567',
    )
