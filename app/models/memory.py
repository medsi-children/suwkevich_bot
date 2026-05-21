from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin


class UserMemory(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "user_memories"

    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="SET NULL"),
        index=True,
    )
    source_message_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        index=True,
    )
    memory_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    memory_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict, nullable=False)
    last_recalled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="memories")

