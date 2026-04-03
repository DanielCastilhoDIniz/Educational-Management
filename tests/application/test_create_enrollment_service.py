from datetime import UTC, datetime

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.errors.persistence_errors import EnrollmentDuplicationError
from application.academic.enrollment.services.create_enrollment import CreateEnrollment
from domain.academic.enrollment.events.enrollment_events import EnrollmentCreated
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from tests.application.fakes import (
    FailingEnrollmentRepository,
    FaillingCreateInRepository,
    InMemoryEnrollmentRepository,
)


def test_create_enrollment_success():
    repo = InMemoryEnrollmentRepository()
    service = CreateEnrollment(repo=repo)

    enrollment = service.execute(
        institution_id="instituion_id",
        student_id="std-1",
        class_group_id="cls-1",
        academic_period_id="acpd-1", 
        actor_id="actor-1",
        occurred_at=datetime.now(UTC)
    )

    assert enrollment is not None
    assert enrollment.success is True
    assert enrollment.new_state == EnrollmentState.ACTIVE
    assert enrollment.domain_events[0].__class__ == EnrollmentCreated
    assert enrollment.domain_events[0].aggregate_id == enrollment.aggregate_id


def test_create_enrollment_duplicate():
    repo = FaillingCreateInRepository(message="Enrollment with the same identifiers already exists.")
    service = CreateEnrollment(repo=repo)

    enrollment = service.execute(
        institution_id="instituion_id",
        student_id="std-1",
        class_group_id="cls-1",
        academic_period_id="acpd-1", 
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
        institution_id="instituion_id",
        student_id="std-1",
        class_group_id="cls-1",
        academic_period_id="acpd-1", 
        actor_id="actor-1",
        occurred_at=datetime.now(UTC)
    )

    assert enrollment is not None
    assert enrollment.success is False
    assert enrollment.error is not None
    assert enrollment.error.code == ErrorCodes.ENROLLMENT_CREATION_FAILED