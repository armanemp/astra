"""Create durable mission and audit tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_durable_missions"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "missions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=True),
        sa.Column("idempotency_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('created','planning','ready','running','retry_wait','verifying',"
            "'awaiting_approval','rejected','released','failed','cancelled','rolled_back')",
            name="ck_missions_status",
        ),
        sa.CheckConstraint("version >= 1", name="ck_missions_version_positive"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_missions_idempotency_key"),
    )
    op.create_index("ix_missions_status", "missions", ["status"], unique=False)
    op.create_table(
        "mission_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("mission_id", sa.String(length=36), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("actor", sa.String(length=128), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("sequence >= 1", name="ck_mission_event_sequence_positive"),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("mission_id", "sequence", name="uq_mission_event_sequence"),
    )
    op.create_index("ix_mission_events_mission_id", "mission_events", ["mission_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_mission_events_mission_id", table_name="mission_events")
    op.drop_table("mission_events")
    op.drop_index("ix_missions_status", table_name="missions")
    op.drop_table("missions")
