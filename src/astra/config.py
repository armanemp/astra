"""Typed and validated application configuration."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

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
    database_url: str = "sqlite:///./astra.db"

    @model_validator(mode="after")
    def validate_runtime_security(self) -> "Settings":
        """Reject unsafe production defaults before the application starts."""
        if self.environment == "production" and self.docs_enabled:
            raise ValueError("ASTRA_DOCS_ENABLED must be false in production")
        if self.environment == "production":
            scheme = urlsplit(self.database_url).scheme
            if scheme not in {"postgresql", "postgresql+psycopg"}:
                raise ValueError("Production ASTRA_DATABASE_URL must use PostgreSQL")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings; tests can clear the cache when changing environment."""
    return Settings()
