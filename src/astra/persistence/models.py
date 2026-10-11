"""SQLAlchemy persistence models for durable mission state and audit history."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Shared metadata root for Alembic and test schemas."""


class MissionRecord(Base):
    """Current mission state. Version is the optimistic-concurrency token."""

    __tablename__ = "missions"
    __table_args__ = (
        CheckConstraint(
            "status IN ('created','planning','ready','running','retry_wait','verifying',"
            "'awaiting_approval','rejected','released','failed','cancelled','rolled_back')",
            name="ck_missions_status",
        ),
        CheckConstraint("version >= 1", name="ck_missions_version_positive"),
        UniqueConstraint("idempotency_key", name="uq_missions_idempotency_key"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created", index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    idempotency_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )
    events: Mapped[list["MissionEventRecord"]] = relationship(
        back_populates="mission",
        cascade="all, delete-orphan",
        order_by="MissionEventRecord.sequence",
    )


class MissionEventRecord(Base):
    """Append-only transition history; each event records the resulting mission version."""

    __tablename__ = "mission_events"
    __table_args__ = (
        UniqueConstraint("mission_id", "sequence", name="uq_mission_event_sequence"),
        CheckConstraint("sequence >= 1", name="ck_mission_event_sequence_positive"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    mission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str] = mapped_column(String(32), nullable=False)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    mission: Mapped[MissionRecord] = relationship(back_populates="events")
