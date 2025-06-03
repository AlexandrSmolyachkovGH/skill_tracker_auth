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
    name: str = Field(
        description='Unique valid username',
        example='Joe_0101',
        min_length=3,
    )
    email: EmailStr = Field(
        description='Unique email address',
        example='joe.0101@example.com',
    )
    password: str = Field(
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


class GetUser(BaseModel):
    id: UUID = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    name: str = Field(
        description='Unique valid username',
        example='Joe_0101',
        min_length=3,
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
    status: StatusEnum = Field(
        description="Active user registration status",
        example='PENDING',
        default=StatusEnum.PENDING,
    )


class PatchUser(BaseModel):
    id: UUID = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    name: Optional[str] = Field(
        description='Unique valid username',
        example='Joe_0101',
        min_length=3,
    )
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
    role: Optional[RoleEnum] = Field(
        description="User role in ['USER', 'ADMIN'] and etc",
        example='USER',
        default=RoleEnum.USER,
    )
    status: Optional[StatusEnum] = Field(
        description="Active user registration status",
        example='PENDING',
        default=StatusEnum.PENDING,
    )


class PutUser(BaseModel):
    id: UUID = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    name: str = Field(
        description='Unique valid username',
        example='Joe_0101',
        min_length=3,
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
    status: StatusEnum = Field(
        description="Active user registration status",
        example='PENDING',
        default=StatusEnum.PENDING,
    )


class DeleteUser(BaseModel):
    id: Optional[UUID] = Field(
        description='Unique user identifier ',
        example='123e4567-e89b-12d3-a456-426614174000',
    )
    name: Optional[str] = Field(
        description='Unique valid username',
        example='Joe_0101',
        min_length=3,
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
