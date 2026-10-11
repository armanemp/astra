"""Initial system endpoints. Business APIs arrive with persistence in a later phase."""

from fastapi import APIRouter
from pydantic import BaseModel

from astra import __version__


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


@router.get("/health/live", response_model=LivenessResponse, tags=["system"])
def liveness() -> LivenessResponse:
    """Report process liveness without external dependencies."""
    return LivenessResponse(version=__version__)


@router.get("/health/ready", response_model=ReadinessResponse, tags=["system"])
def readiness() -> ReadinessResponse:
    """Report readiness of implemented baseline components, without overstating capability."""
    return ReadinessResponse(
        status="ready",
        checks={"api": "ready", "persistence": "not_implemented"},
    )


@router.get("/meta", response_model=MetadataResponse, tags=["system"])
def metadata() -> MetadataResponse:
    """Expose public metadata only; never expose secrets or full settings."""
    return MetadataResponse(
        name="Astra",
        version=__version__,
        capabilities=["health", "mission_lifecycle_contract"],
    )
