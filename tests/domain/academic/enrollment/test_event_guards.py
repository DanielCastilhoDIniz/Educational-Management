from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.errors.enrollment_errors import InvalidStateTransitionError
from domain.academic.enrollment.events.enrollment_events import (
    EnrollmentCancelled,
    EnrollmentConcluded,
    EnrollmentReactivated,
    EnrollmentSuspended,
)
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
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


def test_enrollment_concluded_reject_wrong_state() -> None:

    aggregate_id = "enr-1"
    actor_id = "u-1"

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        EnrollmentConcluded(
            aggregate_id=aggregate_id,
            actor_id=actor_id,
            from_state=EnrollmentState.ACTIVE,
            to_state=EnrollmentState.CANCELLED
        )
    err = exc_info.value
    assert err.details is not None
    assert err.code == "invalid_event_state"
    assert err.details["event"] == "EnrollmentConcluded"
    assert err.details["actual_state"] == EnrollmentState.CANCELLED.value
    assert err.details["expected_state"] == EnrollmentState.CONCLUDED.value


def test_enrollment_cancelled_reject_wrong_state() -> None:

    aggregate_id = "enr-1"
    actor_id = "u-1"

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        EnrollmentCancelled(
            aggregate_id=aggregate_id,
            actor_id=actor_id,
            from_state=EnrollmentState.ACTIVE,
            to_state=EnrollmentState.CONCLUDED
        )
    err = exc_info.value
    assert err.details is not None
    assert err.code == "invalid_event_state"
    assert err.details["event"] == "EnrollmentCancelled"
    assert err.details["actual_state"] == EnrollmentState.CONCLUDED.value
    assert err.details["expected_state"] == EnrollmentState.CANCELLED.value


def test_enrollment_suspended_reject_wrong_state() -> None:

    aggregate_id = "enr-1"
    actor_id = "u-1"

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        EnrollmentSuspended(
            aggregate_id=aggregate_id,
            actor_id=actor_id,
            from_state=EnrollmentState.ACTIVE,
            to_state=EnrollmentState.CONCLUDED
        )
    err = exc_info.value
    assert err.details is not None
    assert err.code == "invalid_event_state"
    assert err.details["event"] == "EnrollmentSuspended"
    assert err.details["actual_state"] == EnrollmentState.CONCLUDED.value
    assert err.details["expected_state"] == EnrollmentState.SUSPENDED.value


def test_enrollment_reactivated_rejects_wrong_target_state() -> None:
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        EnrollmentReactivated(
            aggregate_id="enr-1",
            actor_id="u-1",
            from_state=EnrollmentState.SUSPENDED,
            to_state=EnrollmentState.CONCLUDED,
        )

    err = exc_info.value
    assert err.code == "invalid_event_state"
    assert err.details is not None
    assert err.details["event"] == "EnrollmentReactivated"
    assert err.details["actual_state"] == EnrollmentState.CONCLUDED.value
    assert err.details["expected_state"] == EnrollmentState.ACTIVE.value


def test_enrollment_reactivated_rejects_wrong_origin_state() -> None:
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        EnrollmentReactivated(
            aggregate_id="enr-1",
            actor_id="u-1",
            from_state=EnrollmentState.ACTIVE,
            to_state=EnrollmentState.ACTIVE,
        )

    err = exc_info.value
    assert err.code == "invalid_origin_state"
    assert err.message == "Regra 4.2: Reativação só é permitida a partir do estado TRANCADA."
