"""Contract tests for the initial HTTP surface."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Create an application client per test to avoid shared mutable state."""
    from astra.main import create_app

    return TestClient(create_app())


def test_liveness_does_not_require_dependencies(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"
    assert "version" in response.json()


def test_readiness_is_honest_about_unimplemented_persistence(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"api": "ready", "persistence": "not_implemented"},
    }


def test_metadata_lists_only_implemented_capabilities(client: TestClient) -> None:
    response = client.get("/api/v1/meta")
    assert response.status_code == 200
    assert response.json()["capabilities"] == ["health", "mission_lifecycle_contract"]


def test_interactive_api_docs_are_present_in_development(client: TestClient) -> None:
    assert client.get("/openapi.json").status_code == 200
