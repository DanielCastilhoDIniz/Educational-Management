from datetime import UTC, datetime

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.services.create_enrollment import CreateEnrollment
from domain.academic.enrollment.events.enrollment_events import EnrollmentCreated
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from tests.application.academic.enrollment.fakes import (
    FailingEnrollmentRepository,
    InMemoryEnrollmentRepository,
)


def test_create_enrollment_success():
    repo = InMemoryEnrollmentRepository()
    service = CreateEnrollment(repo=repo)

    enrollment = service.execute(
        institution_id="institution_id",
        student_id="std-1",
        class_group_id="cls-1",
        academic_period_id="acp-1", 
        actor_id="actor-1",
        occurred_at=datetime.now(UTC)
    )

    assert enrollment is not None
    assert enrollment.success is True
    assert enrollment.new_state == EnrollmentState.ACTIVE
    assert enrollment.domain_events[0].__class__ == EnrollmentCreated
    assert enrollment.domain_events[0].aggregate_id == enrollment.aggregate_id


def test_create_enrollment_duplicate():
    repo = InMemoryEnrollmentRepository()
    service = CreateEnrollment(repo=repo)

    enrollment1 = service.execute(
        institution_id="institution_id",
        student_id="std-1",
        class_group_id="cls-1",
        academic_period_id="acp-1", 
        actor_id="actor-1",
        occurred_at=datetime.now(UTC)
    )
    assert enrollment1 is not None
    assert enrollment1.success is True
    assert enrollment1.new_state == EnrollmentState.ACTIVE

    enrollment = service.execute(
        institution_id="institution_id",
        student_id="std-1",
        class_group_id="cls-1",
        academic_period_id="acp-1", 
        actor_id="actor-1",
        occurred_at=datetime.now(UTC)
    )

    assert enrollment is not None
    assert enrollment.success is False
    assert enrollment.error is not None
    assert enrollment.error.code == ErrorCodes.DUPLICATE_ENROLLMENT

def test_create_enrollment_infrastructure_failure():
    repo = FailingEnrollmentRepository(
        message="Failed to create enrollment due to an infrastructure error.")
    service = CreateEnrollment(repo=repo)

    enrollment = service.execute(
        institution_id="institution_id",
        student_id="std-1",
        class_group_id="cls-1",
        academic_period_id="acp-1", 
        actor_id="actor-1",
        occurred_at=datetime.now(UTC)
    )

    assert enrollment is not None
    assert enrollment.success is False
    assert enrollment.error is not None
    assert enrollment.error.code == ErrorCodes.ENROLLMENT_CREATION_FAILED