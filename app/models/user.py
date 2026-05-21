from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UuidPrimaryKeyMixin


class User(UuidPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(128), index=True)
    first_name: Mapped[str | None] = mapped_column(String(256))
    language_code: Mapped[str | None] = mapped_column(String(16))
    profile_summary: Mapped[str | None] = mapped_column(Text)
    support_preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    risk_notes: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    sessions = relationship("ConversationSession", back_populates="user")
    messages = relationship("Message", back_populates="user")
    memories = relationship("UserMemory", back_populates="user")
    important_facts = relationship("ImportantFact")
    known_people = relationship("KnownPerson")
    open_topics = relationship("OpenTopic")
