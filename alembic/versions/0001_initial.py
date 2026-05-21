"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-21 18:45:00
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True, unique=True),
        sa.Column("username", sa.String(length=128), nullable=True),
        sa.Column("first_name", sa.String(length=256), nullable=True),
        sa.Column("language_code", sa.String(length=16), nullable=True),
        sa.Column("profile_summary", sa.Text(), nullable=True),
        sa.Column(
            "support_preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("risk_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=False)

    op.create_table(
        "sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="telegram"),
        sa.Column("state", sa.String(length=64), nullable=False, server_default="active"),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_messages_session_id", "messages", ["session_id"], unique=False)
    op.create_index("ix_messages_user_id", "messages", ["user_id"], unique=False)

    op.create_table(
        "user_memories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sessions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "source_message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("messages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("memory_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("importance", sa.Integer(), nullable=False, server_default="3"),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("last_recalled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_user_memories_user_id", "user_memories", ["user_id"], unique=False)
    op.create_index("ix_user_memories_session_id", "user_memories", ["session_id"], unique=False)
    op.create_index(
        "ix_user_memories_source_message_id",
        "user_memories",
        ["source_message_id"],
        unique=False,
    )
    op.create_index("ix_user_memories_memory_type", "user_memories", ["memory_type"], unique=False)


def downgrade() -> None:
    op.drop_table("user_memories")
    op.drop_table("messages")
    op.drop_table("sessions")
    op.drop_table("users")
