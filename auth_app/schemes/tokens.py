from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from auth_app.schemes.users import (
    CreateUserScheme,
    RoleEnum,
)


class RoleDataScheme(CreateUserScheme):
    admin_secret: Optional[str] = Field(
        description='Explicit admin key',
        example='123Admin',
        default=None,
    )


class CreateDataScheme(BaseModel):
    user_id: UUID | str = Field(
        description='Unique user identifier',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    email: EmailStr = Field(
        description='Unique email address',
        example='joe.0101@example.com',
    )
    role: RoleEnum = Field(
        description='User role',
        example='USER',
        default=RoleEnum.USER,
    )
    admin_secret: Optional[str] = Field(
        description='Secret key to get admin settings',
        example='123example%!',
        default=None,
    )

    class Config:
        from_attributes = True


class CreateRefreshScheme(BaseModel):
    user_id: UUID | str = Field(
        description='Unique user identifier',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    token: str = Field(
        description='Refresh user token',
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...',
    )
    expires_at: datetime = Field(
        description='Date and time of token activity',
        example='2025-01-01T15:34:00',
    )

    class Config:
        from_attributes = True


class GetRefreshScheme(BaseModel):
    id: UUID = Field(
        description='Unique token identifier',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    user_id: UUID = Field(
        description='User identifier references the token',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    token: str = Field(
        description='Refresh user token',
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...',
    )
    expires_at: datetime = Field(
        description='Date and time of token activity',
        example='2025-01-01T15:34:00',
    )

    class Config:
        from_attributes = True


class DeleteRefreshScheme(BaseModel):
    email: EmailStr = Field(
        description='Email address of verified account',
        example='joe.0101@example.com',
    )
    password_hash: str = Field(
        description='Password of verified account',
        example='MySecurePassword123!',
        min_length=6,
        max_length=100,
    )

    class Config:
        from_attributes = True


class UpdateRefreshScheme(BaseModel):
    token: str = Field(
        description='Refresh user token',
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...',
    )
    expires_at: datetime = Field(
        description='Date and time of token activity',
        example='2025-01-01T15:34:00',
    )

    class Config:
        from_attributes = True


class CreateAccessScheme(BaseModel):
    refresh_token: str = Field(
        description='Refresh user token',
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...',
    )

    class Config:
        from_attributes = True


class GetAccessScheme(BaseModel):
    message: dict[str, str] = Field(
        description='Access user token',
        example="{'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...'}",
    )

    class Config:
        from_attributes = True
