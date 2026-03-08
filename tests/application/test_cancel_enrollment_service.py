from datetime import datetime, timezone

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.services.cancel_enrollment import CancelEnrollmentService
from domain.academic.enrollment.events.enrollment_events import EnrollmentCancelled
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from tests.application.fakes import (
    FailingEnrollmentRepository,
    InMemoryEnrollmentRepository,
    ScriptedEnrollment,
    make_cancelled_event,
    make_enrollment,
)


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
    assert result.success is True
    assert len(result.domain_events) == 1

    event = result.domain_events[0]
    assert isinstance(event, EnrollmentCancelled)

    assert result.changed is True
    assert result.aggregate_id == enrollment.id

    assert result.new_state == EnrollmentState.CANCELLED
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

    result = service.execute(
        enrollment_id="enr-missing",
        actor_id="user-1",
        justification="valid justification",
        occurred_at=datetime.now(timezone.utc)
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.ENROLLMENT_NOT_FOUND
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

    assert result.success is True
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
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

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="",
        occurred_at=datetime.now(timezone.utc),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.JUSTIFICATION_REQUIRED
    assert repo.save_calls == 0

    persisted_enrollment = repo.get_by_id(enrollment.id)
    assert persisted_enrollment is not None
    assert persisted_enrollment.state == EnrollmentState.ACTIVE
    assert persisted_enrollment.suspended_at is None


def test_cancel_enrollment_returns_unexpected_error_when_save_fails():
    repo = FailingEnrollmentRepository(message="db down")
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    repo.seed(enrollment)

    service = CancelEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="valid justification",
        occurred_at=datetime.now(timezone.utc),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.UNEXPECTED_ERROR
    assert repo.save_calls == 1
    assert enrollment.state == EnrollmentState.CANCELLED
    assert len(enrollment.peek_domain_events()) == 1


def test_cancel_enrollment_returns_integrity_violation_when_event_exists_without_state_change():
    repo = InMemoryEnrollmentRepository()
    enrollment = ScriptedEnrollment(
        enrollment_id="enr-1",
        state=EnrollmentState.ACTIVE,
        next_state=EnrollmentState.ACTIVE,
        command_events=[make_cancelled_event()],
    )
    repo.seed(enrollment)

    service = CancelEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id="enr-1",
        actor_id="user-1",
        justification="valid justification",
        occurred_at=datetime.now(timezone.utc),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.STATE_INTEGRITY_VIOLATION
    assert result.error.details["reason"] == "event_without_state_change"
    assert repo.save_calls == 0


def test_cancel_enrollment_returns_integrity_violation_when_state_changes_without_event():
    repo = InMemoryEnrollmentRepository()
    enrollment = ScriptedEnrollment(
        enrollment_id="enr-1",
        state=EnrollmentState.ACTIVE,
        next_state=EnrollmentState.CANCELLED,
        command_events=[],
    )
    repo.seed(enrollment)

    service = CancelEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id="enr-1",
        actor_id="user-1",
        justification="valid justification",
        occurred_at=datetime.now(timezone.utc),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.STATE_INTEGRITY_VIOLATION
    assert result.error.details["reason"] == "state_changed_without_event"
    assert repo.save_calls == 0
