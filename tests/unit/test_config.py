"""Tests for fail-safe configuration defaults."""

import pytest
from pydantic import ValidationError

from astra.config import Settings


def test_defaults_are_development_safe() -> None:
    settings = Settings()
    assert settings.environment == "development"
    assert settings.api_prefix == "/api/v1"
    assert settings.docs_enabled is True


def test_production_rejects_interactive_docs() -> None:
    with pytest.raises(ValidationError, match="ASTRA_DOCS_ENABLED"):
        Settings(environment="production", docs_enabled=True)


def test_production_can_disable_interactive_docs() -> None:
    settings = Settings(environment="production", docs_enabled=False)
    assert settings.docs_enabled is False


def test_invalid_api_prefix_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(api_prefix="not-an-absolute-path")
