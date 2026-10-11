"""Mission lifecycle vocabulary and invariant checks.

This module contains domain rules only. It does not persist state or execute tasks.
"""

from enum import StrEnum


class MissionStatus(StrEnum):
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    VERIFYING = "verifying"
    AWAITING_APPROVAL = "awaiting_approval"
    REJECTED = "rejected"
    RELEASED = "released"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class InvalidMissionTransition(ValueError):
    """Raised when a requested mission status transition violates the state machine."""


_ALLOWED_TRANSITIONS: dict[MissionStatus, frozenset[MissionStatus]] = {
    MissionStatus.CREATED: frozenset({MissionStatus.PLANNING, MissionStatus.CANCELLED}),
    MissionStatus.PLANNING: frozenset(
        {MissionStatus.READY, MissionStatus.FAILED, MissionStatus.CANCELLED}
    ),
    MissionStatus.READY: frozenset({MissionStatus.RUNNING, MissionStatus.CANCELLED}),
    MissionStatus.RUNNING: frozenset(
        {MissionStatus.VERIFYING, MissionStatus.RETRY_WAIT, MissionStatus.FAILED, MissionStatus.CANCELLED}
    ),
    MissionStatus.RETRY_WAIT: frozenset(
        {MissionStatus.RUNNING, MissionStatus.FAILED, MissionStatus.CANCELLED}
    ),
    MissionStatus.VERIFYING: frozenset(
        {MissionStatus.AWAITING_APPROVAL, MissionStatus.REJECTED, MissionStatus.FAILED}
    ),
    MissionStatus.AWAITING_APPROVAL: frozenset(
        {MissionStatus.RELEASED, MissionStatus.REJECTED, MissionStatus.CANCELLED}
    ),
    MissionStatus.REJECTED: frozenset({MissionStatus.RUNNING, MissionStatus.CANCELLED}),
    MissionStatus.RELEASED: frozenset({MissionStatus.ROLLED_BACK}),
    MissionStatus.FAILED: frozenset(),
    MissionStatus.CANCELLED: frozenset(),
    MissionStatus.ROLLED_BACK: frozenset(),
}


def transition_mission(current: MissionStatus, target: MissionStatus) -> MissionStatus:
    """Validate and return a target state without mutating external state."""
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise InvalidMissionTransition(f"Transition not allowed: {current.value} -> {target.value}")
    return target


def allowed_mission_transitions(current: MissionStatus) -> frozenset[MissionStatus]:
    """Return the immutable set of allowed next states."""
    return _ALLOWED_TRANSITIONS[current]
