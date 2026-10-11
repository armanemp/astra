"""Typed and validated application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables with the ASTRA_ prefix."""

    model_config = SettingsConfigDict(
        env_prefix="ASTRA_",
        env_file=None,
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Astra"
    environment: Literal["development", "test", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    api_prefix: str = Field(
        default="/api/v1",
        pattern=r"^/(?:[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*)?$",
    )
    docs_enabled: bool = True

    @model_validator(mode="after")
    def disable_interactive_docs_in_production(self) -> "Settings":
        """Require explicit safe configuration: API docs must be disabled in production."""
        if self.environment == "production" and self.docs_enabled:
            raise ValueError("ASTRA_DOCS_ENABLED must be false in production")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings; tests can clear the cache when changing environment."""
    return Settings()
