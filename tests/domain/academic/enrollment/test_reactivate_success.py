from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.errors.enrollment_errors import (
    InvalidStateTransitionError,
    JustificationRequiredError,
)
from domain.academic.enrollment.events.enrollment_events import EnrollmentReactivated
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    now = datetime.now(timezone.utc)
    cancelled_at = now if state == EnrollmentState.CANCELLED else None
    concluded_at = now if state == EnrollmentState.CONCLUDED else None
    suspended_at = now if state == EnrollmentState.SUSPENDED else None

    return Enrollment(
        id="enr-1",
        institution_id="inst-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        cancelled_at=cancelled_at,
        concluded_at=concluded_at,
        suspended_at=suspended_at,
    )


def test_reactivate_from_suspended_success() -> None:
    enrollment = make_enrollment(state=EnrollmentState.SUSPENDED)
    actor_id = "u-1"
    justification = "motivo válido"
    occurred_at = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    enrollment.reactivate(
        actor_id=actor_id,
        justification=justification,
        occurred_at=occurred_at,
    )

    assert enrollment.state == EnrollmentState.ACTIVE
    assert enrollment.suspended_at is None
    assert enrollment.concluded_at is None
    assert enrollment.cancelled_at is None

    assert len(enrollment.transitions) == 1
    transition = enrollment.transitions[0]
    assert transition.from_state == EnrollmentState.SUSPENDED
    assert transition.to_state == EnrollmentState.ACTIVE
    assert transition.actor_id == actor_id
    assert transition.justification == justification
    assert transition.occurred_at == occurred_at

    assert len(enrollment._domain_events) == 1
    event = enrollment._domain_events[0]
    assert isinstance(event, EnrollmentReactivated)
    assert event.from_state == EnrollmentState.SUSPENDED
    assert event.to_state == EnrollmentState.ACTIVE
    assert event.actor_id == actor_id
    assert event.justification == justification
    assert event.occurred_at == occurred_at


def test_reactivate_is_idempotent_when_already_active() -> None:
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    state_before = enrollment.state
    transitions_before = list(enrollment.transitions)
    events_before = list(enrollment._domain_events)

    enrollment.reactivate(
        actor_id="u-1",
        justification="motivo válido",
    )

    assert enrollment.state == state_before
    assert enrollment.transitions == transitions_before
    assert enrollment._domain_events == events_before


def test_reactivate_from_cancelled_raises_invalid_transition() -> None:
    enrollment = make_enrollment(state=EnrollmentState.CANCELLED)

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        enrollment.reactivate(
            actor_id="u-1",
            justification="motivo válido",
        )

    err = exc_info.value
    assert err.code == "invalid_state_transition"
    assert err.details is not None
    assert err.details["current_state"] == EnrollmentState.CANCELLED.value
    assert err.details["required_state"] == EnrollmentState.SUSPENDED.value
    assert err.details["attempted_action"] == "reactivate"
    assert err.details["allowed_from_states"] == [EnrollmentState.SUSPENDED.value]


def test_reactivate_requires_justification() -> None:
    enrollment = make_enrollment(state=EnrollmentState.SUSPENDED)

    with pytest.raises(JustificationRequiredError) as exc_info:
        enrollment.reactivate(
            actor_id="u-1",
            justification="",
        )

    err = exc_info.value
    assert err.code == "justification_required"
    assert err.message == "Justification is required to reactivate enrollment."
    assert err.details is not None
    assert err.details["policy"] == "justification_required"
    assert err.details["attempted_action"] == "reactivate"
