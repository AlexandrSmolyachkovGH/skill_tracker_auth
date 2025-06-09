import uuid
from enum import Enum

from sqlalchemy import Boolean, Column
from sqlalchemy import Enum as Enum_Sql
from sqlalchemy import String, Table
from sqlalchemy.dialects.postgresql import UUID

from auth_app.models.meta import metadata_obj


class UserRole(str, Enum):
    ADMIN = 'ADMIN'
    USER = 'USER'
    STAFFER = 'STAFFER'
    OTHER = 'OTHER'


users = Table(
    "users",
    metadata_obj,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("email", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("role", Enum_Sql(UserRole), nullable=False, default=UserRole.USER),
    Column("is_verified", Boolean, default=False),
    Column("is_active", Boolean, default=True),
)
