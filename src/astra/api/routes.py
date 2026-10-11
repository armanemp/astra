"""System endpoints and application health contracts."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from astra import __version__
from astra.api.missions import persistence_check, router as missions_router
from astra.persistence.database import get_session


class LivenessResponse(BaseModel):
    status: str = "alive"
    version: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict[str, str]


class MetadataResponse(BaseModel):
    name: str
    version: str
    api_version: str = "v1"
    capabilities: list[str]


router = APIRouter()
router.include_router(missions_router)


@router.get("/health/live", response_model=LivenessResponse, tags=["system"])
def liveness() -> LivenessResponse:
    """Report process liveness without external dependencies."""
    return LivenessResponse(version=__version__)


@router.get("/health/ready", response_model=ReadinessResponse, tags=["system"])
def readiness(session: Session = Depends(get_session)) -> ReadinessResponse:
    """Report readiness based on the actual persistence dependency."""
    checks = persistence_check(session)
    return ReadinessResponse(
        status="ready" if checks["database"] == "ready" else "not_ready",
        checks={"api": "ready", **checks},
    )


@router.get("/meta", response_model=MetadataResponse, tags=["system"])
def metadata() -> MetadataResponse:
    """Expose implemented capabilities only; never expose secrets or full settings."""
    return MetadataResponse(
        name="Astra",
        version=__version__,
        capabilities=["health", "mission_lifecycle_contract", "durable_missions", "mission_audit"],
    )
