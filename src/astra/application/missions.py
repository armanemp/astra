"""Transactional mission use cases."""

import hashlib
import json
from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from astra.domain.missions import InvalidMissionTransition, MissionStatus, transition_mission
from astra.persistence.models import MissionEventRecord, MissionRecord


class MissionNotFound(LookupError):
    """The requested mission does not exist."""


class MissionConflict(ValueError):
    """The requested operation conflicts with existing state."""


class MissionReleaseBlocked(PermissionError):
    """Release is blocked until a human approval mechanism is implemented."""


@dataclass(frozen=True, slots=True)
class MissionInput:
    title: str
    description: str = ""


def _payload_hash(payload: MissionInput) -> str:
    canonical = json.dumps(
        {"title": payload.title, "description": payload.description},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def create_mission(session: Session, payload: MissionInput, idempotency_key: str) -> tuple[MissionRecord, bool]:
    """Create once per key; replaying the same request returns the original resource."""
    digest = _payload_hash(payload)
    existing = session.scalar(
        select(MissionRecord).where(MissionRecord.idempotency_key == idempotency_key)
    )
    if existing is not None:
        if existing.idempotency_hash != digest:
            raise MissionConflict("Idempotency-Key was already used with a different request body")
        return existing, False

    mission = MissionRecord(
        title=payload.title,
        description=payload.description,
        status=MissionStatus.CREATED.value,
        version=1,
        idempotency_key=idempotency_key,
        idempotency_hash=digest,
    )
    mission.events.append(
        MissionEventRecord(
            sequence=1,
            from_status=None,
            to_status=MissionStatus.CREATED.value,
            actor="system",
            reason="Mission created",
        )
    )
    session.add(mission)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing = session.scalar(
            select(MissionRecord).where(MissionRecord.idempotency_key == idempotency_key)
        )
        if existing is None:
            raise
        if existing.idempotency_hash != digest:
            raise MissionConflict("Idempotency-Key was already used with a different request body")
        return existing, False
    session.refresh(mission)
    return mission, True


def get_mission(session: Session, mission_id: str) -> MissionRecord:
    """Load one mission with its ordered audit history."""
    mission = session.scalar(
        select(MissionRecord)
        .options(selectinload(MissionRecord.events))
        .where(MissionRecord.id == mission_id)
    )
    if mission is None:
        raise MissionNotFound(mission_id)
    return mission


def list_missions(session: Session, limit: int = 50, offset: int = 0) -> list[MissionRecord]:
    """Return a bounded, newest-first mission page."""
    statement = (
        select(MissionRecord)
        .order_by(MissionRecord.created_at.desc(), MissionRecord.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement).all())


def transition_existing_mission(
    session: Session,
    mission_id: str,
    target: MissionStatus,
    expected_version: int,
    actor: str,
    reason: str = "",
) -> MissionRecord:
    """Atomically update state and append an event using optimistic concurrency."""
    if target in {MissionStatus.RELEASED, MissionStatus.ROLLED_BACK}:
        raise MissionReleaseBlocked(
            "Release/rollback endpoints remain disabled until authenticated human approval "
            "and a verified release controller are implemented"
        )
    mission = get_mission(session, mission_id)
    current = MissionStatus(mission.status)
    if mission.version != expected_version:
        raise MissionConflict(
            f"Stale mission version: expected {expected_version}, current {mission.version}"
        )
    try:
        transition_mission(current, target)
    except InvalidMissionTransition as exc:
        raise MissionConflict(str(exc)) from exc

    next_version = mission.version + 1
    result = session.execute(
        update(MissionRecord)
        .where(MissionRecord.id == mission_id, MissionRecord.version == expected_version)
        .values(status=target.value, version=next_version)
    )
    if result.rowcount != 1:
        session.rollback()
        raise MissionConflict("Mission changed concurrently; reload and retry")
    session.add(
        MissionEventRecord(
            mission_id=mission_id,
            sequence=next_version,
            from_status=current.value,
            to_status=target.value,
            actor=actor,
            reason=reason,
        )
    )
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise MissionConflict("Mission event could not be committed; reload and retry") from exc
    return get_mission(session, mission_id)
