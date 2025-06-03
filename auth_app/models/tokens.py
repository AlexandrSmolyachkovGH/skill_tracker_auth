import uuid
from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID

metadata_obj = MetaData()


def expire_date(n_days: int = 30) -> datetime:
    return datetime.utcnow() + timedelta(n_days)


refresh_tokens = Table(
    "refresh_tokens",
    metadata_obj,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("token", String, unique=True, nullable=False),
    Column("expires_at", DateTime, nullable=False, default=expire_date),
)
