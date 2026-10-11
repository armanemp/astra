"""Persistence boundary tests."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from astra.api.missions import persistence_check
from astra.persistence import database


@pytest.mark.parametrize(
    ("url", "expected_driver"),
    [
        ("sqlite:///./astra-test.db", "sqlite"),
        ("postgresql://user:pass@localhost/astra", "postgresql+psycopg"),
    ],
)
def test_engine_uses_configured_driver(
    monkeypatch: pytest.MonkeyPatch,
    url: str,
    expected_driver: str,
) -> None:
    database.get_engine.cache_clear()
    monkeypatch.setattr(database, "get_settings", lambda: SimpleNamespace(database_url=url))
    engine = database.get_engine()
    try:
        assert engine.url.drivername == expected_driver
    finally:
        engine.dispose()
        database.get_engine.cache_clear()


def test_persistence_check_reports_database_failure() -> None:
    session = Mock(spec=Session)
    session.execute.side_effect = OperationalError("SELECT 1", {}, RuntimeError("offline"))
    assert persistence_check(session) == {"database": "unavailable"}
