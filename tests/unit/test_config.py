"""Tests for fail-safe configuration defaults."""

import pytest
from pydantic import ValidationError

from astra.config import Settings


def test_defaults_are_development_safe() -> None:
    settings = Settings()
    assert settings.environment == "development"
    assert settings.api_prefix == "/api/v1"
    assert settings.docs_enabled is True
    assert settings.database_url.startswith("sqlite:")


def test_production_rejects_interactive_docs() -> None:
    with pytest.raises(ValidationError, match="ASTRA_DOCS_ENABLED"):
        Settings(environment="production", docs_enabled=True)


def test_production_can_disable_interactive_docs() -> None:
    settings = Settings(
        environment="production",
        docs_enabled=False,
        database_url="postgresql+psycopg://user:pass@localhost/astra",
    )
    assert settings.docs_enabled is False


def test_production_rejects_non_postgresql_database() -> None:
    with pytest.raises(ValidationError, match="must use PostgreSQL"):
        Settings(environment="production", docs_enabled=False, database_url="sqlite:///astra.db")


def test_invalid_api_prefix_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(api_prefix="not-an-absolute-path")
