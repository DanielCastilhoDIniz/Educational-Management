import uuid

import pytest
from apps.academic.repositories.django_enrollment_repository import DjangoEnrollmentRepository

from infrastructureTests.factory.new_enrollment_factory import (
    factory_create_new_enrrolment_for_tests,
)


@pytest.mark.django_db
def test_get_by_id_snapshot_is_none_when_enrollment_does_not_exist() -> None:
    repository = DjangoEnrollmentRepository()
    result = repository.get_by_id(str(uuid.uuid4()))
    assert result is None


@pytest.mark.django_db
def test_get_by_id_success() -> None:
    enrollment = factory_create_new_enrrolment_for_tests()
    repository = DjangoEnrollmentRepository()
    result = repository.get_by_id(enrollment_id=str(enrollment.id))
    assert result is not None
    assert result.id == str(enrollment.id)
    assert result.student_id == str(enrollment.student_id)
    assert result.class_group_id == str(enrollment.class_group_id)
    assert result.academic_period_id == str(enrollment.academic_period_id)
    assert result.created_at == enrollment.created_at
    assert result.state.value == enrollment.state



