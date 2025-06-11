from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AuthData(BaseModel):
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


class CreateRefresh(BaseModel):
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


class GetRefresh(BaseModel):
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


class DeleteRefresh(BaseModel):
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


class UpdateRefresh(BaseModel):
    token: str = Field(
        description='Refresh user token',
        example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ...',
    )
