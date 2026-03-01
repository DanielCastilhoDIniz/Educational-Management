from datetime import datetime, timezone

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.services.conclude_enrollment import ConcludeEnrollmentService
from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from tests.application.fakes import (
    FailingEnrollmentRepository,
    InMemoryEnrollmentRepository,
    ScriptedEnrollment,
    make_concluded_event,
    make_enrollment,
)


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


def test_conclude_enrollment_returns_unexpected_error_when_save_fails():
    repo = FailingEnrollmentRepository(message="db down")
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    repo.seed(enrollment)

    service = ConcludeEnrollmentService(repo=repo)
    verdict = ConclusionVerdict.allowed()

    result = service.execute(
        enrollment_id=enrollment.id,
        actor_id="user-1",
        verdict=verdict,
        occurred_at=datetime.now(timezone.utc),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.UNEXPECTED_ERROR
    assert repo.save_calls == 1
    assert enrollment.state == EnrollmentState.CONCLUDED
    assert len(enrollment.peek_domain_events()) == 1


def test_conclude_enrollment_returns_integrity_violation_when_event_exists_without_state_change():
    repo = InMemoryEnrollmentRepository()
    enrollment = ScriptedEnrollment(
        enrollment_id="enr-1",
        state=EnrollmentState.ACTIVE,
        next_state=EnrollmentState.ACTIVE,
        command_events=[make_concluded_event()],
    )
    repo.seed(enrollment)

    service = ConcludeEnrollmentService(repo=repo)
    verdict = ConclusionVerdict.allowed()

    result = service.execute(
        enrollment_id="enr-1",
        actor_id="user-1",
        verdict=verdict,
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


def test_conclude_enrollment_returns_integrity_violation_when_state_changes_without_event():
    repo = InMemoryEnrollmentRepository()
    enrollment = ScriptedEnrollment(
        enrollment_id="enr-1",
        state=EnrollmentState.ACTIVE,
        next_state=EnrollmentState.CONCLUDED,
        command_events=[],
    )
    repo.seed(enrollment)

    service = ConcludeEnrollmentService(repo=repo)
    verdict = ConclusionVerdict.allowed()

    result = service.execute(
        enrollment_id="enr-1",
        actor_id="user-1",
        verdict=verdict,
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
