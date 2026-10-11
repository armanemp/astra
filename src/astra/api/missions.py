"""Versioned mission HTTP API."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from astra.application.missions import (
    MissionConflict,
    MissionInput,
    MissionNotFound,
    MissionReleaseBlocked,
    create_mission,
    get_mission,
    list_missions,
    transition_existing_mission,
)
from astra.domain.missions import MissionStatus
from astra.persistence.database import get_session
from astra.persistence.models import MissionRecord


class MissionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)


class MissionTransition(BaseModel):
    target: MissionStatus
    expected_version: int = Field(ge=1)
    actor: str = Field(min_length=1, max_length=128)
    reason: str = Field(default="", max_length=2_000)


class MissionEventResponse(BaseModel):
    sequence: int
    from_status: MissionStatus | None
    to_status: MissionStatus
    actor: str
    reason: str
    occurred_at: datetime


class MissionResponse(BaseModel):
    id: str
    title: str
    description: str
    status: MissionStatus
    version: int
    created_at: datetime
    updated_at: datetime
    events: list[MissionEventResponse] = Field(default_factory=list)


router = APIRouter(prefix="/missions", tags=["missions"])


def _response(mission: MissionRecord) -> MissionResponse:
    return MissionResponse(
        id=mission.id,
        title=mission.title,
        description=mission.description,
        status=MissionStatus(mission.status),
        version=mission.version,
        created_at=mission.created_at,
        updated_at=mission.updated_at,
        events=[
            MissionEventResponse(
                sequence=event.sequence,
                from_status=MissionStatus(event.from_status) if event.from_status else None,
                to_status=MissionStatus(event.to_status),
                actor=event.actor,
                reason=event.reason,
                occurred_at=event.occurred_at,
            )
            for event in mission.events
        ],
    )


@router.get("", response_model=list[MissionResponse])
def missions_list(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    session: Session = Depends(get_session),
) -> list[MissionResponse]:
    """List missions with bounded pagination."""
    try:
        return [_response(item) for item in list_missions(session, limit, offset)]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Mission storage unavailable") from exc


@router.post("", response_model=MissionResponse)
def missions_create(
    payload: MissionCreate,
    response: Response,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=255)],
    session: Session = Depends(get_session),
) -> MissionResponse:
    """Create a mission idempotently; retries with the same key do not duplicate it."""
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title must not be blank")
    try:
        mission, created = create_mission(
            session,
            MissionInput(title=title, description=payload.description),
            idempotency_key,
        )
        response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return _response(get_mission(session, mission.id))
    except MissionConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Mission storage unavailable") from exc


@router.get("/{mission_id}", response_model=MissionResponse)
def missions_get(mission_id: str, session: Session = Depends(get_session)) -> MissionResponse:
    """Get mission state and ordered transition history."""
    try:
        return _response(get_mission(session, mission_id))
    except MissionNotFound as exc:
        raise HTTPException(status_code=404, detail="Mission not found") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Mission storage unavailable") from exc


@router.post("/{mission_id}/transitions", response_model=MissionResponse)
def missions_transition(
    mission_id: str,
    payload: MissionTransition,
    session: Session = Depends(get_session),
) -> MissionResponse:
    """Apply a guarded, versioned state transition."""
    try:
        mission = transition_existing_mission(
            session,
            mission_id,
            payload.target,
            payload.expected_version,
            payload.actor,
            payload.reason,
        )
        return _response(mission)
    except MissionNotFound as exc:
        raise HTTPException(status_code=404, detail="Mission not found") from exc
    except MissionReleaseBlocked as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except MissionConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=503, detail="Mission storage unavailable") from exc


def persistence_check(session: Session) -> dict[str, str]:
    """Check actual database connectivity for readiness reporting."""
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return {"database": "unavailable"}
    return {"database": "ready"}
