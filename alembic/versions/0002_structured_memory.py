"""structured memory

Revision ID: 0002_structured_memory
Revises: 0001_initial
Create Date: 2026-05-21 20:10:00
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002_structured_memory"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
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
    ]


def upgrade() -> None:
    op.create_table(
        "important_facts",
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
            "source_message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("messages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("fact_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("importance", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("sensitivity", sa.String(length=32), nullable=False, server_default="normal"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "first_mentioned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_mentioned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        *_timestamps(),
    )
    op.create_index("ix_important_facts_user_id", "important_facts", ["user_id"])
    op.create_index(
        "ix_important_facts_source_message_id",
        "important_facts",
        ["source_message_id"],
    )
    op.create_index("ix_important_facts_fact_type", "important_facts", ["fact_type"])
    op.create_index("ix_important_facts_is_active", "important_facts", ["is_active"])

    op.create_table(
        "known_people",
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
            "source_message_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("messages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=True),
        sa.Column("relation_summary", sa.Text(), nullable=True),
        sa.Column("emotional_context", sa.Text(), nullable=True),
        sa.Column("importance", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "first_mentioned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "last_mentioned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        *_timestamps(),
    )
    op.create_index("ix_known_people_user_id", "known_people", ["user_id"])
    op.create_index("ix_known_people_source_message_id", "known_people", ["source_message_id"])
    op.create_index("ix_known_people_name", "known_people", ["name"])
    op.create_index("ix_known_people_is_active", "known_people", ["is_active"])

    op.create_table(
        "open_topics",
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
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("next_step", sa.Text(), nullable=True),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "last_mentioned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        *_timestamps(),
    )
    op.create_index("ix_open_topics_user_id", "open_topics", ["user_id"])
    op.create_index("ix_open_topics_session_id", "open_topics", ["session_id"])
    op.create_index("ix_open_topics_source_message_id", "open_topics", ["source_message_id"])
    op.create_index("ix_open_topics_status", "open_topics", ["status"])


def downgrade() -> None:
    op.drop_table("open_topics")
    op.drop_table("known_people")
    op.drop_table("important_facts")

