"""Integration-style API tests using an isolated SQLite database."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from astra.config import Settings
from astra.main import create_app
from astra.persistence.database import get_session
from astra.persistence.models import Base


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a fresh schema and app dependency override for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_session() -> Generator[Session, None, None]:
        with factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_create_is_idempotent_and_audited(client: TestClient) -> None:
    headers = {"Idempotency-Key": "create-mission-0001"}
    body = {"title": "Inspect failing tests", "description": "Reproduce before patching"}
    first = client.post("/api/v1/missions", headers=headers, json=body)
    replay = client.post("/api/v1/missions", headers=headers, json=body)
    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["id"] == replay.json()["id"]
    assert len(first.json()["events"]) == 1
    assert first.json()["events"][0]["to_status"] == "created"


def test_idempotency_key_cannot_be_reused_for_different_payload(client: TestClient) -> None:
    headers = {"Idempotency-Key": "create-mission-0002"}
    created = client.post("/api/v1/missions", headers=headers, json={"title": "One"})
    assert created.status_code == 201
    conflict = client.post("/api/v1/missions", headers=headers, json={"title": "Two"})
    assert conflict.status_code == 409


def test_blank_title_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/missions",
        headers={"Idempotency-Key": "create-mission-blank"},
        json={"title": "   "},
    )
    assert response.status_code == 422


def test_get_unknown_mission_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/missions/not-a-real-mission")
    assert response.status_code == 404


def test_transition_checks_state_version_and_appends_event(client: TestClient) -> None:
    created = client.post(
        "/api/v1/missions",
        headers={"Idempotency-Key": "create-mission-0003"},
        json={"title": "State transition"},
    ).json()
    url = f"/api/v1/missions/{created['id']}/transitions"
    payload = {
        "target": "planning",
        "expected_version": 1,
        "actor": "test",
        "reason": "start planning",
    }
    changed = client.post(url, json=payload)
    assert changed.status_code == 200
    assert changed.json()["status"] == "planning"
    assert changed.json()["version"] == 2
    assert len(changed.json()["events"]) == 2
    stale = client.post(url, json=payload)
    assert stale.status_code == 409


def test_invalid_domain_transition_is_rejected(client: TestClient) -> None:
    created = client.post(
        "/api/v1/missions",
        headers={"Idempotency-Key": "create-mission-invalid"},
        json={"title": "No skipping"},
    ).json()
    response = client.post(
        f"/api/v1/missions/{created['id']}/transitions",
        json={"target": "ready", "expected_version": 1, "actor": "test"},
    )
    assert response.status_code == 409
    assert client.get(f"/api/v1/missions/{created['id']}").json()["status"] == "created"


def test_release_is_blocked_without_human_approval_service(client: TestClient) -> None:
    created = client.post(
        "/api/v1/missions",
        headers={"Idempotency-Key": "create-mission-0004"},
        json={"title": "No skipping"},
    ).json()
    response = client.post(
        f"/api/v1/missions/{created['id']}/transitions",
        json={"target": "released", "expected_version": 1, "actor": "test"},
    )
    assert response.status_code == 403
    current = client.get(f"/api/v1/missions/{created['id']}")
    assert current.json()["status"] == "created"
    assert current.json()["version"] == 1


def test_list_pagination_is_bounded(client: TestClient) -> None:
    for i in range(3):
        response = client.post(
            "/api/v1/missions",
            headers={"Idempotency-Key": f"create-mission-page-{i:02d}"},
            json={"title": f"Mission {i}"},
        )
        assert response.status_code == 201
    page = client.get("/api/v1/missions?limit=2&offset=1")
    assert page.status_code == 200
    assert len(page.json()) == 2


def test_readiness_reports_live_persistence(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["checks"]["database"] == "ready"


def test_production_does_not_expose_unauthenticated_mission_api() -> None:
    app = create_app(
        Settings(
            environment="production",
            docs_enabled=False,
            database_url="postgresql+psycopg://user:pass@localhost/astra",
        )
    )
    client = TestClient(app)
    assert client.get("/api/v1/missions").status_code == 404
    assert client.get("/openapi.json").status_code == 404
