from datetime import UTC, datetime

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.services.reactivate_enrollment import (
    ReactivateEnrollmentService,
)
from domain.academic.enrollment.events.enrollment_events import EnrollmentReactivated
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from tests.application.fakes import (
    FailingEnrollmentRepository,
    InMemoryEnrollmentRepository,
    ScriptedEnrollment,
    make_enrollment,
    make_reactivated_event,
)


def test_reactivate_enrollment_success():
    repo = InMemoryEnrollmentRepository()
    enrollment = make_enrollment(state=EnrollmentState.SUSPENDED)

    service = ReactivateEnrollmentService(repo=repo)
    repo.save(enrollment)
    repo.save_calls = 0

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="reactivate justification"

    )
    assert result.success is True
    assert len(result.domain_events) == 1

    event = result.domain_events[0]
    assert isinstance(event, EnrollmentReactivated)

    assert result.changed is True
    assert result.aggregate_id == enrollment.id

    assert result.new_state == EnrollmentState.ACTIVE
    assert event.from_state.value == EnrollmentState.SUSPENDED.value
    assert event.to_state.value == EnrollmentState.ACTIVE.value

    assert repo.save_calls == 1

    persisted_enrollment = repo.get_by_id(enrollment.id)
    assert persisted_enrollment is not None
    assert persisted_enrollment.state == EnrollmentState.ACTIVE
    assert persisted_enrollment.reactivated_at is not None

    assert enrollment.suspended_at is None
    assert enrollment.concluded_at is None
    assert enrollment.cancelled_at is None
    assert enrollment.reactivated_at is not None




def test_reactivate_enrollment_not_found():
    repo = InMemoryEnrollmentRepository()
    service = ReactivateEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id="enr-missing",
        actor_id="user-1",
        justification="reactivate justification"
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.ENROLLMENT_NOT_FOUND
    assert repo.save_calls == 0


def test_reactivate_enrollment_idempotent_when_already_active():
    repo = InMemoryEnrollmentRepository()

    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
   
    repo.save(enrollment)
    repo.save_calls = 0

    service = ReactivateEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="reactivate justification"
    )

    assert result.success is True
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert repo.save_calls == 0

    persisted_enrollment = repo.get_by_id(enrollment.id)
    assert persisted_enrollment is not None

    assert persisted_enrollment.state == EnrollmentState.ACTIVE
    

def test_reactivate_enrollment_returns_unexpected_error_when_save_fails():
    repo = FailingEnrollmentRepository(message="db down")
    enrollment = make_enrollment(state=EnrollmentState.SUSPENDED)
    repo.seed(enrollment)

    service = ReactivateEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="reactivate justification"
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.DATABASE_ERROR
    assert repo.save_calls == 1
    assert enrollment.state == EnrollmentState.ACTIVE
    assert len(enrollment.peek_domain_events()) == 1


def test_reactivate_enrollment_returns_integrity_violation_when_event_exists_without_state_change():
    repo = InMemoryEnrollmentRepository()
    enrollment = ScriptedEnrollment(
        enrollment_id="enr-1",
        state=EnrollmentState.ACTIVE,
        next_state=EnrollmentState.ACTIVE,
        command_events=[make_reactivated_event()],
    )
    repo.seed(enrollment)

    service = ReactivateEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id="enr-1",
        actor_id="user-1",
        justification="reactivate justification",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.STATE_INTEGRITY_VIOLATION
    details = result.error.details
    assert details is not None
    assert details["reason"] == "event_without_state_change"
    assert repo.save_calls == 0

def test_reactivate_enrollment_returns_failure_when_enrollment_is_not_suspended():
    repo = InMemoryEnrollmentRepository()
    enrollment = make_enrollment(state=EnrollmentState.CANCELLED)
    repo.seed(enrollment)

    service = ReactivateEnrollmentService(repo=repo)
   
    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        justification="reactivate justification",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.INVALID_STATE_TRANSITION
    assert result.error.message == "Cannot reactivate enrollment from state cancelled."
    details = result.error.details
    assert details is not None
    assert details["aggregate_id"] == enrollment.id
    assert details["action"] == "reactivate"
    assert details["current_state"] == EnrollmentState.CANCELLED.value
    assert details["domain_code"] == "invalid_state_transition"
    assert details["attempted_action"] == "reactivate"
    assert details["required_state"] == EnrollmentState.SUSPENDED.value
    assert repo.save_calls == 0

    persisted = repo.get_by_id(enrollment.id)
    assert persisted is not None
    assert persisted.state == EnrollmentState.CANCELLED


def test_reactivate_enrollment_returns_integrity_violation_when_state_changes_without_event():
    repo = InMemoryEnrollmentRepository()
    enrollment = ScriptedEnrollment(
        enrollment_id="enr-1",
        state=EnrollmentState.SUSPENDED,
        next_state=EnrollmentState.ACTIVE,
        command_events=[],
    )
    repo.seed(enrollment)

    service = ReactivateEnrollmentService(repo=repo)

    result = service.execute(
        enrollment_id="enr-1",
        actor_id="user-1",
        justification="reactivate justification",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.STATE_INTEGRITY_VIOLATION
    details = result.error.details
    assert details is not None
    assert details["reason"] == "state_changed_without_event"
    assert repo.save_calls == 0
