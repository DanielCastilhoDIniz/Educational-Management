from datetime import datetime, timezone

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import EnrollmentConcluded
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
    now = datetime.now(timezone.utc)
    cancelled_at = now if state == EnrollmentState.CANCELLED else None
    concluded_at = now if state == EnrollmentState.CONCLUDED else None
    suspended_at = now if state == EnrollmentState.SUSPENDED else None

    return Enrollment(
        id="enr-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        cancelled_at=cancelled_at,
        concluded_at=concluded_at,
        suspended_at=suspended_at,
    )


def test_is_final_when_concluded() -> None:
    enrollment = make_enrollment(state=EnrollmentState.CONCLUDED)

    enrollment_is_final = enrollment.is_final()

    assert enrollment_is_final is True


def test_is_final_when_cancelled() -> None:
    enrollment = make_enrollment(state=EnrollmentState.CANCELLED)

    enrollment_is_final = enrollment.is_final()

    assert enrollment_is_final is True


def test_is_final_when_active() -> None:
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)

    enrollment_is_final = enrollment.is_final()

    assert enrollment_is_final is False


def test_is_final_when_suspended() -> None:
    enrollment = make_enrollment(state=EnrollmentState.SUSPENDED)

    enrollment_is_final = enrollment.is_final()

    assert enrollment_is_final is False
