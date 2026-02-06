from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import EnrollmentConcluded
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict
from domain.academic.enrollment.errors.enrollment_errors import InvalidStateTransitionError


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
    now = datetime.now(timezone.utc)

    concluded_at = now if state == EnrollmentState.CONCLUDED else None

    return Enrollment(
        id="enr-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        concluded_at=concluded_at,
    )


def assert_conclude_success(
        enrollment: Enrollment,
        *,
        expected_from: EnrollmentState,
        actor_id: str,
        expected_occurred_at: datetime,
        justification: str | None = None
        ):
    """Asserts comuns para cenários de conclusão com sucesso"""

    assert enrollment.state == EnrollmentState.CONCLUDED

    assert enrollment.concluded_at is not None
    assert enrollment.concluded_at == expected_occurred_at

    # transitions
    assert len(enrollment.transitions) == 1
    t = enrollment.transitions[-1]
    assert t.from_state == expected_from
    assert t.to_state == EnrollmentState.CONCLUDED
    assert t.actor_id == actor_id
    assert t.justification == justification
    assert t.occurred_at == expected_occurred_at

    # events
    assert len(enrollment._domain_events) == 1
    e = enrollment._domain_events[-1]
    assert isinstance(e, EnrollmentConcluded)
    assert e.aggregate_id == enrollment.id
    assert e.from_state == expected_from
    assert e.to_state == EnrollmentState.CONCLUDED
    assert e.actor_id == actor_id
    assert e.justification == justification
    assert e.occurred_at is not None
    assert e.occurred_at == expected_occurred_at

    assert e.occurred_at == t.occurred_at


def test_conclude_from_active_success() -> None:

    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    occurred_at = datetime.now(timezone.utc)
    justification = None
    verdict = ConclusionVerdict()

    # Act
    enrollment.conclude(
        actor_id=actor_id,
        occurred_at=occurred_at,    
        justification=justification,
        verdict=verdict
    )

    assert_conclude_success(
        enrollment=enrollment,
        expected_from=EnrollmentState.ACTIVE,
        actor_id=actor_id,
        expected_occurred_at=occurred_at,
        justification=justification
    )