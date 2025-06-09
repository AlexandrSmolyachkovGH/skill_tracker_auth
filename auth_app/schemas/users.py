from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class StatusEnum(str, Enum):
    PENDING = 'PENDING'
    VERIFIED = 'VERIFIED'
    DENIED = 'DENIED'


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


class CreateUser(BaseModel):
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
    role: Optional[RoleEnum] = Field(
        description="User role in ['USER', 'ADMIN'] and etc",
        example='USER',
        default=RoleEnum.USER,
    )


class GetUser(BaseModel):
    id: UUID = Field(
        description='Unique user identifier',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
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
    role: RoleEnum = Field(
        description="User role in ['USER', 'ADMIN'] and etc",
        example='USER',
        default=RoleEnum.USER,
    )
    is_verified: bool = Field(
        description="Verification status",
        example=True,
        default=StatusEnum.PENDING,
    )
    is_active: bool = Field(
        description="Activity status",
        example=True,
        default=StatusEnum.PENDING,
    )


class PatchUser(BaseModel):
    email: Optional[EmailStr] = Field(
        description='Unique email address',
        example='joe.0101@example.com',
    )
    password_hash: Optional[str] = Field(
        description='Password of the user',
        example='MySecurePassword123!',
        min_length=6,
        max_length=100,
    )


class PutUser(BaseModel):
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


class DeleteUser(BaseModel):
    id: Optional[UUID] = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    email: Optional[EmailStr] = Field(
        description='Unique email address',
        example='joe.0101@example.com',
    )
    password_hash: str = Field(
        description='Password of the user',
        example='MySecurePassword123!',
        min_length=6,
        max_length=100,
        default='',
    )


class UserFilter(BaseModel):
    id: Optional[UUID] = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    email: Optional[EmailStr] = Field(
        description='Unique email address',
        example='joe.0101@example.com',
    )
