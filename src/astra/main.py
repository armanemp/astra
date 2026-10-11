"""FastAPI application factory and ASGI entry point."""

from fastapi import FastAPI

from astra import __version__
from astra.api.routes import router
from astra.config import get_settings


def create_app() -> FastAPI:
    """Create an application with validated configuration captured at startup."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version=__version__,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    application.include_router(router, prefix=settings.api_prefix)
    return application


app = create_app()
