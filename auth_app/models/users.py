import uuid
from enum import Enum

from sqlalchemy import Boolean
from sqlalchemy import Enum as Enum_Sql
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from auth_app.models.base import Base


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    STAFFER = 'STAFFER'
    OTHER = 'OTHER'


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum_Sql(UserRole), nullable=False, default=UserRole.USER)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    refresh_tokens: Mapped[list["RefreshTokenORM"]] = relationship("RefreshTokenORM", back_populates="user")
