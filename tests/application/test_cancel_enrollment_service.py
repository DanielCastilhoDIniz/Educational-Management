from datetime import datetime, timezone
from application.academic.enrollment.services.cancel_enrollment import CancelEnrollmentService
from application.academic.enrollment.errors.enrollment_errors import EnrollmentNotFoundError

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.academic.enrollment.errors.enrollment_errors import JustificationRequiredError

import pytest


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


def test_cancel_enrollment_success():
    repo = InMemoryEnrollmentRepository()
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)

    service = CancelEnrollmentService(repo=repo)
    repo.save(enrollment)
    repo.save_calls = 0

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="valid justification",
        occurred_at=datetime.now(timezone.utc)
    )
    assert len(result.events) == 1

    event = result.events[0]

    assert result.changed is True
    assert result.aggregate_id == enrollment.id

    assert result.new_state == EnrollmentState.CANCELLED.value
    assert event.from_state.value == EnrollmentState.ACTIVE.value
    assert event.to_state.value == EnrollmentState.CANCELLED.value

    assert repo.save_calls == 1

    persisted_enrollment = repo.get_by_id(enrollment.id)
    assert persisted_enrollment is not None
    assert persisted_enrollment.state == EnrollmentState.CANCELLED
    assert persisted_enrollment.cancelled_at is not None


def test_cancel_enrollment_not_found():
    repo = InMemoryEnrollmentRepository()
    service = CancelEnrollmentService(repo=repo)

    with pytest.raises(EnrollmentNotFoundError):
        service.execute(
            enrollment_id="enr-missing",
            actor_id="user-1",
            justification="valid justification",
            occurred_at=datetime.now(timezone.utc)
        )

    assert repo.save_calls == 0


def test_cancel_enrollment_idempotent_when_already_cancelled():
    repo = InMemoryEnrollmentRepository()

    enrollment = make_enrollment(state=EnrollmentState.CANCELLED)
    original_cancelled_at = enrollment.cancelled_at

    repo.save(enrollment)
    repo.save_calls = 0

    service = CancelEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="valid Justification",
        occurred_at=datetime.now(timezone.utc)
    )

    assert result.changed is False
    assert result.events == []
    assert repo.save_calls == 0

    persisted_enrollment = repo.get_by_id(enrollment.id)

    assert persisted_enrollment.state == EnrollmentState.CANCELLED
    assert persisted_enrollment.cancelled_at == original_cancelled_at


def test_cancel_enrollment_requires_justification():
    repo = InMemoryEnrollmentRepository()

    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    repo.save(enrollment)
    repo.save_calls = 0

    service = CancelEnrollmentService(repo=repo)

    with pytest.raises(JustificationRequiredError):
        service.execute(
            enrollment_id=enrollment.id,
            actor_id="user-1",
            justification="",
            occurred_at=datetime.now(timezone.utc),
        )

    assert repo.save_calls == 0

    persisted_enrollment = repo.get_by_id(enrollment.id)
    assert persisted_enrollment is not None
    assert persisted_enrollment.state == EnrollmentState.ACTIVE
    assert persisted_enrollment.suspended_at is None
