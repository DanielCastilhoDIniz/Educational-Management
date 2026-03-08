from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.errors.enrollment_errors import DomainError
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.academic.enrollment.value_objects.state_transition import StateTransition


def test_rejects_none_occurred_at() -> None:
    with pytest.raises(DomainError) as exc_info:
        StateTransition(
            from_state=EnrollmentState.ACTIVE,
            actor_id="user-1",
            to_state=EnrollmentState.SUSPENDED,
            occurred_at=None,
        )

    err = exc_info.value
    assert err.code == "invalid_occurred_at"
    assert err.message == "occurred_at cannot be None"
    assert err.details is not None
    assert err.details["reasons"] is None


def test_rejects_empty_actor_id() -> None:
    with pytest.raises(DomainError) as exc_info:
        StateTransition(
            from_state=EnrollmentState.ACTIVE,
            actor_id="   ",
            to_state=EnrollmentState.SUSPENDED,
            occurred_at=datetime.now(timezone.utc),
        )

    err = exc_info.value
    assert err.code == "invalid_actor_id"
    assert err.message == "actor_id cannot be empty"
    assert err.details is not None
    assert err.details["reasons"] == "   "


def test_normalizes_naive_occurred_at_to_utc() -> None:
    occurred_at = datetime(2026, 1, 15, 10, 30, 0)

    transition = StateTransition(
        from_state=EnrollmentState.ACTIVE,
        actor_id="user-1",
        to_state=EnrollmentState.SUSPENDED,
        occurred_at=occurred_at,
    )

    assert transition.occurred_at.tzinfo == timezone.utc
    assert transition.occurred_at == occurred_at.replace(tzinfo=timezone.utc)


def test_rejects_same_from_and_to_state() -> None:
    with pytest.raises(DomainError) as exc_info:
        StateTransition(
            from_state=EnrollmentState.ACTIVE,
            actor_id="user-1",
            to_state=EnrollmentState.ACTIVE,
            occurred_at=datetime.now(timezone.utc),
        )

    err = exc_info.value
    assert err.code == "invalid_state_transition"
    assert err.message == "from_state and to_state cannot be the same"
    assert err.details is not None
    assert err.details["from_state"] == EnrollmentState.ACTIVE.value
    assert err.details["to_state"] == EnrollmentState.ACTIVE.value
