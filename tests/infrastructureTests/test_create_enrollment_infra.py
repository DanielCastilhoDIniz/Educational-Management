from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel
from apps.academic.repositories.django_enrollment_repository import DjangoEnrollmentRepository
from django.db import DatabaseError

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.errors.persistence_errors import (
    EnrollmentDuplicationError,
    EnrollmentTechnicalPersistenceError,
)
from domain.academic.enrollment.entities.enrollment import Enrollment


@pytest.mark.django_db
def test_create_enrollment_infra_success():
    enrollment = Enrollment.create(
        institution_id="00000000-0000-0000-0000-000000000001",
        student_id="00000000-0000-0000-0000-000000000002",
        class_group_id="00000000-0000-0000-0000-000000000003",
        academic_period_id="00000000-0000-0000-0000-000000000004",
        actor_id="00000000-0000-0000-0000-000000000005",
        occurred_at=datetime.now(UTC),
    )
    assert enrollment is not None

    repo = DjangoEnrollmentRepository()
    version = repo.create(enrollment)

    saved = EnrollmentModel.objects.get(id=enrollment.id)


    assert saved is not None
    assert str(saved.id) == enrollment.id
    assert str(saved.institution_id) == enrollment.institution_id
    assert str(saved.student_id) == enrollment.student_id
    assert str(saved.class_group_id) == enrollment.class_group_id
    assert str(saved.academic_period_id) == enrollment.academic_period_id
    assert str(saved.created_by) == enrollment.created_by
    assert str(saved.state) == enrollment.state.value
    assert saved.created_at == enrollment.created_at
    assert EnrollmentTransitionModel.objects.count() == 0
    assert saved.version == enrollment.version
    assert enrollment.version == 1
    assert version == 1


@pytest.mark.django_db
def test_create_enrollment_infra_duplicate():
    enrollment1 = Enrollment.create(
        institution_id="00000000-0000-0000-0000-000000000001",
        student_id="00000000-0000-0000-0000-000000000002",
        class_group_id="00000000-0000-0000-0000-000000000003",
        academic_period_id="00000000-0000-0000-0000-000000000004",
        actor_id="00000000-0000-0000-0000-000000000005",
        occurred_at=datetime.now(UTC),
    )
    repo = DjangoEnrollmentRepository()
    repo.create(enrollment1)

    enrollment2 = Enrollment.create(
        institution_id="00000000-0000-0000-0000-000000000001",
        student_id="00000000-0000-0000-0000-000000000002",
        class_group_id="00000000-0000-0000-0000-000000000003",
        academic_period_id="00000000-0000-0000-0000-000000000004",
        actor_id="00000000-0000-0000-0000-000000000005",
        occurred_at=datetime.now(UTC),
    )
  

    with pytest.raises(EnrollmentDuplicationError) as exc_info:
        repo.create(enrollment2)

    assert exc_info.value.code == ErrorCodes.DUPLICATE_ENROLLMENT
    assert exc_info.value.message == "An enrollment with the same identifiers already exists."
    assert exc_info.value.details == {
        "constraint": "unique_enrollment",
    }

@pytest.mark.django_db
def test_create_enrollment_infra_fail_raises_EnrollmentTechnicalPersistenceError():
    enrollment = Enrollment.create(
        institution_id="00000000-0000-0000-0000-000000000001",
        student_id="00000000-0000-0000-0000-000000000002",
        class_group_id="00000000-0000-0000-0000-000000000003",
        academic_period_id="00000000-0000-0000-0000-000000000004",
        actor_id="00000000-0000-0000-0000-000000000005",
        occurred_at=datetime.now(UTC),
    )
    repo = DjangoEnrollmentRepository()
    assert enrollment is not None

    with patch("apps.academic.models.enrollment_model.EnrollmentModel.save", side_effect=DatabaseError("db error")):
        with pytest.raises(EnrollmentTechnicalPersistenceError) as exc_info:
            repo.create(enrollment)
    
    assert exc_info.value.code == ErrorCodes.DATABASE_ERROR
    assert exc_info.value.message == "Failed to create enrollment due to a database error."
    assert exc_info.value.details == {"error": "db error"}
    
@pytest.mark.django_db
def test_create_enrollment_with_enrollment_keys_collision():
    enrollment1 = Enrollment.create(
        institution_id="00000000-0000-0000-0000-000000000001",
        student_id="00000000-0000-0000-0000-000000000002",
        class_group_id="00000000-0000-0000-0000-000000000003",
        academic_period_id="00000000-0000-0000-0000-000000000004",
        actor_id="00000000-0000-0000-0000-000000000005",
        occurred_at=datetime.now(UTC),
    )
    repo = DjangoEnrollmentRepository()
    repo.create(enrollment1)

    enrollment2 = Enrollment.create(
        institution_id="11111111-1111-1111-1111-111111111111",
        student_id="22222222-2222-2222-2222-222222222222",
        class_group_id="33333333-3333-3333-3333-333333333333",
        academic_period_id="44444444-4444-4444-4444-444444444444",
        actor_id="55555555-5555-5555-5555-555555555555",
        occurred_at=datetime.now(UTC),
    )
    enrollment2.id = enrollment1.id  # Force ID collision

    with pytest.raises(EnrollmentDuplicationError) as exc_info:
        repo.create(enrollment2)

    assert exc_info.value.code == ErrorCodes.DUPLICATE_ENROLLMENT
    assert exc_info.value.message == "An enrollment with the same identifiers already exists."
    assert exc_info.value.details == {
        "constraint": "enrollments_pkey",
    }



  