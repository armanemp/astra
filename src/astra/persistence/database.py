"""Database engine/session lifecycle."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from astra.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Create one process-wide engine; production configuration is validated at startup."""
    url = get_settings().database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    options: dict[str, object] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    return create_engine(url, **options)


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    """Return the canonical session factory."""
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that always closes the session."""
    with get_session_factory()() as session:
        yield session
