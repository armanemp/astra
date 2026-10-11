"""Production-dialect tests, enabled only in the dedicated PostgreSQL CI job."""

import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from astra.application.missions import (
    MissionConflict,
    MissionInput,
    create_mission,
    get_mission,
    transition_existing_mission,
)
from astra.domain.missions import MissionStatus
from astra.persistence.database import get_engine, get_session_factory


pytestmark = pytest.mark.skipif(
    os.getenv("ASTRA_RUN_POSTGRES_INTEGRATION") != "1",
    reason="requires the dedicated PostgreSQL integration job",
)


def _factory() -> sessionmaker[Session]:
    """Return the real PostgreSQL session factory configured for this job."""
    return get_session_factory()


def test_clean_database_has_expected_alembic_revision() -> None:
    with get_engine().connect() as connection:
        revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert revision == "0001_durable_missions"


def test_mission_and_audit_persist_across_sessions_and_replays() -> None:
    factory = _factory()
    key = f"pg-mission-{uuid4().hex}"
    payload = MissionInput(title="PostgreSQL durability", description="Verify independent sessions")

    with factory() as first_session:
        created, is_new = create_mission(first_session, payload, key)
        assert is_new is True
        mission_id = created.id

    with factory() as second_session:
        persisted = get_mission(second_session, mission_id)
        assert persisted.status == MissionStatus.CREATED.value
        assert persisted.version == 1
        assert len(persisted.events) == 1
        assert persisted.events[0].to_status == MissionStatus.CREATED.value

        replay, is_new = create_mission(second_session, payload, key)
        assert is_new is False
        assert replay.id == mission_id

        with pytest.raises(MissionConflict, match="different request body"):
            create_mission(second_session, MissionInput(title="Different payload"), key)


def test_stale_concurrent_transition_is_rejected_across_sessions() -> None:
    factory = _factory()
    key = f"pg-race-{uuid4().hex}"
    with factory() as creator:
        mission, _ = create_mission(creator, MissionInput(title="Concurrent update"), key)
        mission_id = mission.id

    first = factory()
    second = factory()
    try:
        observed = get_mission(first, mission_id)
        assert observed.version == 1

        transition_existing_mission(
            second,
            mission_id,
            MissionStatus.PLANNING,
            expected_version=1,
            actor="postgres-integration-test",
            reason="advance state in second session",
        )

        with pytest.raises(MissionConflict, match="Stale mission version"):
            transition_existing_mission(
                first,
                mission_id,
                MissionStatus.READY,
                expected_version=1,
                actor="postgres-integration-test",
                reason="stale update must not win",
            )

        with factory() as verifier:
            persisted = get_mission(verifier, mission_id)
            assert persisted.status == MissionStatus.PLANNING.value
            assert persisted.version == 2
            assert [event.sequence for event in persisted.events] == [1, 2]
    finally:
        first.close()
        second.close()
