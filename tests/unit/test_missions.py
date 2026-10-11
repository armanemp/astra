"""Tests for mission state-machine invariants."""

import pytest

from astra.domain.missions import (
    InvalidMissionTransition,
    MissionStatus,
    allowed_mission_transitions,
    transition_mission,
)


def test_happy_path_requires_verification_and_approval() -> None:
    current = MissionStatus.CREATED
    for target in (
        MissionStatus.PLANNING,
        MissionStatus.READY,
        MissionStatus.RUNNING,
        MissionStatus.VERIFYING,
        MissionStatus.AWAITING_APPROVAL,
        MissionStatus.RELEASED,
    ):
        current = transition_mission(current, target)
    assert current is MissionStatus.RELEASED


def test_cannot_release_without_verification_and_approval() -> None:
    with pytest.raises(InvalidMissionTransition):
        transition_mission(MissionStatus.RUNNING, MissionStatus.RELEASED)


def test_terminal_failure_cannot_be_restarted() -> None:
    with pytest.raises(InvalidMissionTransition):
        transition_mission(MissionStatus.FAILED, MissionStatus.RUNNING)


def test_release_can_only_move_to_rollback() -> None:
    assert allowed_mission_transitions(MissionStatus.RELEASED) == frozenset(
        {MissionStatus.ROLLED_BACK}
    )
    with pytest.raises(InvalidMissionTransition):
        transition_mission(MissionStatus.RELEASED, MissionStatus.RUNNING)


def test_rejected_change_may_be_reworked_or_cancelled() -> None:
    assert allowed_mission_transitions(MissionStatus.REJECTED) == frozenset(
        {MissionStatus.RUNNING, MissionStatus.CANCELLED}
    )
