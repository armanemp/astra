"""FastAPI application factory and ASGI entry point."""

from fastapi import FastAPI

from astra import __version__
from astra.api.missions import router as missions_router
from astra.api.routes import router
from astra.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an app; unauthenticated mission mutations are disabled in production."""
    runtime_settings = settings or get_settings()
    application = FastAPI(
        title=runtime_settings.app_name,
        version=__version__,
        docs_url="/docs" if runtime_settings.docs_enabled else None,
        redoc_url="/redoc" if runtime_settings.docs_enabled else None,
        openapi_url="/openapi.json" if runtime_settings.docs_enabled else None,
    )
    application.include_router(router, prefix=runtime_settings.api_prefix)
    if runtime_settings.environment != "production":
        application.include_router(missions_router, prefix=runtime_settings.api_prefix)
    return application


app = create_app()
