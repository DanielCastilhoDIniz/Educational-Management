from datetime import datetime, timezone
from application.academic.enrollment.services.conclude_enrollment import ConcludeEnrollmentService
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
    now = datetime.now(timezone.utc)

    concluded_at = now if state == EnrollmentState.CONCLUDED else None
    suspended_at = now if state == EnrollmentState.SUSPENDED else None
    cancelled_at = now if state == EnrollmentState.CANCELLED else None

    return Enrollment(
        id="enr-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        concluded_at=concluded_at,
        suspended_at=suspended_at,
        cancelled_at=cancelled_at
    )


class InMemoryEnrollmentRepository:
    def __init__(self):
        self.items: dict[str, Enrollment] = {}
        self.save_calls: int = 0

    def get_by_id(self, enrollment_id: str) -> Enrollment | None:
        return self.items.get(enrollment_id)

    def save(self, enrollment: Enrollment) -> None:
        self.items[enrollment.id] = enrollment
        self.save_calls += 1


def test_conclude_enrollment_success():
    repo = InMemoryEnrollmentRepository()
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)

    verdict = ConclusionVerdict(is_allowed=True, requires_justification=False, reasons=[])
    service = ConcludeEnrollmentService(repo=repo)
    repo.save(enrollment)
    repo.save_calls = 0

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        verdict=verdict
    )
    assert result.success is True
    assert len(result.domain_events) == 1

    event = result.domain_events[0]

    assert result.changed is True
    assert result.aggregate_id == enrollment.id

    assert result.new_state == EnrollmentState.CONCLUDED
    assert event.from_state.value == EnrollmentState.ACTIVE.value
    assert event.to_state.value == EnrollmentState.CONCLUDED.value

    assert repo.save_calls == 1

    persisted_enrollment = repo.get_by_id(enrollment.id)
    assert persisted_enrollment is not None
    assert persisted_enrollment.state == EnrollmentState.CONCLUDED
    assert persisted_enrollment.concluded_at is not None


def test_conclude_enrollment_not_found():
    repo = InMemoryEnrollmentRepository()
    service = ConcludeEnrollmentService(repo=repo)

    verdict = ConclusionVerdict(is_allowed=True, requires_justification=False, reasons=[])

    result = service.execute(
        enrollment_id="enr-missing",
        actor_id="user-1",
        verdict=verdict,
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.ENROLLMENT_NOT_FOUND
    assert repo.save_calls == 0


def test_conclude_enrollment_idempotent_when_already_concluded():
    repo = InMemoryEnrollmentRepository()

    enrollment = make_enrollment(state=EnrollmentState.CONCLUDED)
    original_concluded_at = enrollment.concluded_at

    repo.save(enrollment)
    repo.save_calls = 0

    service = ConcludeEnrollmentService(repo=repo)

    verdict = ConclusionVerdict(
        is_allowed=True,
        requires_justification=False,
        reasons=[]
    )

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        verdict=verdict,
    )

    assert result.success is True
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert repo.save_calls == 0

    persisted_enrollment = repo.get_by_id(enrollment.id)

    assert persisted_enrollment.state == EnrollmentState.CONCLUDED
    assert persisted_enrollment.concluded_at == original_concluded_at
