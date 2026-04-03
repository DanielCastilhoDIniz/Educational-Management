
from datetime import UTC, datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.errors.enrollment_errors import (
    DomainError,
    InvalidStateTransitionError,
    JustificationRequiredError,
)
from domain.academic.enrollment.events.enrollment_events import EnrollmentCreated
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def test_create_enrollment_has_unique_id() -> None:
       # Arrange:    
    enrolment = Enrollment.create(
        institution_id="inst-1",
        student_id="std-1",
        class_group_id="class-1",
        academic_period_id="academic_period_1",
        actor_id="actor_id",
        occurred_at=datetime.now(UTC)
    )

    assert enrolment.id is not None
    assert isinstance(enrolment.id, str) is not None

def test_create_enrollment_has_initial_state_active() -> None:
       # Arrange:
        enrolment = Enrollment.create(
        institution_id="inst-1",
        student_id="std-1",
        class_group_id="class-1",
        academic_period_id="academic_period_1",
        actor_id="actor_id",
        occurred_at=datetime.now(UTC)
    )

        assert enrolment.state == EnrollmentState.ACTIVE

def test_create_enrollmet_has_bufered_event() -> None:
        # Arrange:
        enrollment = Enrollment.create(
        institution_id="inst-1",
        student_id="std-1",
        class_group_id="class-1",
        academic_period_id="academic_period_1",
        actor_id="actor_id",
        occurred_at=datetime.now(UTC)
    )
        
        assert len(enrollment._domain_events) == 1
        e = enrollment._domain_events[-1]

        assert isinstance(e, EnrollmentCreated)
        assert e.aggregate_id == enrollment.id
        assert e.actor_id == "actor_id"
        assert e.institution_id == "inst-1"
        assert e.student_id == "std-1"
        assert e.class_group_id == "class-1"
        assert e.academic_period_id == "academic_period_1"
        assert e.occurred_at is not None
        assert e.occurred_at == enrollment.created_at
        assert e.event_id is not None

def test_create_enrollment_field_reactivate_at_is_none() -> None:

        # Arrange:
        enrollment = Enrollment.create(
        institution_id="inst-1",
        student_id="std-1",
        class_group_id="class-1",
        academic_period_id="academic_period_1",
        actor_id="actor_id",
        occurred_at=datetime.now(UTC)
    )
        assert enrollment.reactivated_at is None













