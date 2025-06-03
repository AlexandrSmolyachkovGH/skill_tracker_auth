import uuid

from sqlalchemy import Boolean, Column, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID

metadata_obj = MetaData()

users = Table(
    "users",
    metadata_obj,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("email", String, unique=True, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("is_verified", Boolean, default=False),
    Column("is_active", Boolean, default=True),
)
