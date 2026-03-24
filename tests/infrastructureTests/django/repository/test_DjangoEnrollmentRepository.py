import uuid
from datetime import UTC, datetime

import pytest
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel
from apps.academic.repositories.django_enrollment_repository import DjangoEnrollmentRepository

from infrastructure.errors.persistence_errors import ConcurrencyConflictError
from infrastructureTests.factory.new_enrollment_factory import (
    factory_create_new_enrrolment_for_tests,
)


@pytest.mark.django_db(transaction=True)
def test_get_by_id_snapshot_is_none_when_enrollment_does_not_exist() -> None:
    repository = DjangoEnrollmentRepository()
    result = repository.get_by_id(str(uuid.uuid4()))
    assert result is None


@pytest.mark.django_db(transaction=True)
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


@pytest.mark.django_db(transaction=True)
def test_save_return_cuncurrency_conflict_error() -> None:
    enrollment = factory_create_new_enrrolment_for_tests()
    repository = DjangoEnrollmentRepository()
    result_one = repository.get_by_id(enrollment_id=str(enrollment.id))

    assert result_one is not None

    result_one.suspend(actor_id="actor-1", justification="justification", occurred_at=datetime.now(UTC))  
  
    restult_two = EnrollmentModel.objects.get(id=str(enrollment.id))
    restult_two.version += 1
    restult_two.save()
    
    with pytest.raises(ConcurrencyConflictError) as e:
            repository.save(result_one)

    assert e.value.code == "version_mismatch"
    assert e.value.message in "The enrollment exists, but its persisted version \
                                  does not match the aggregate origin version."
    assert e.value.details is not None
    assert e.value.details["expected_version"] == result_one.version
    assert e.value.details["aggregate_id"] == str(enrollment.id)

@pytest.mark.django_db(transaction=True)
def test_save_success() -> None:
    enrollment = factory_create_new_enrrolment_for_tests()
    repository = DjangoEnrollmentRepository()
    result_before = repository.get_by_id(enrollment_id=str(enrollment.id))
    enrollment_before = EnrollmentModel.objects.get(id=str(enrollment.id))

    assert result_before is not None

    result_before.suspend(actor_id=str(uuid.uuid4()), justification="justification", occurred_at=datetime.now(UTC))
    
    new_version = repository.save(result_before)


    enrollment_after = EnrollmentModel.objects.get(id=str(enrollment.id))

    assert enrollment_before.state == "active"
    assert enrollment_before.concluded_at is None
    assert enrollment_before.cancelled_at is None
    assert enrollment_before.suspended_at is None
    assert enrollment_before.updated_at is not None

    assert new_version == enrollment_before.version + 1
    assert enrollment_after.version == enrollment_before.version +1
    assert enrollment_after.state == "suspended"
    assert enrollment_after.suspended_at is not None
    assert enrollment_after.concluded_at is None
    assert enrollment_after.cancelled_at is None
    assert enrollment_after.updated_at is not None
    assert enrollment_after.created_at == enrollment_before.created_at
    assert enrollment_after.student_id == enrollment_before.student_id
    assert enrollment_after.class_group_id == enrollment_before.class_group_id
    assert enrollment_after.academic_period_id == enrollment_before.academic_period_id
    assert enrollment_after.id == enrollment_before.id

    transition = EnrollmentTransitionModel.objects.filter(enrollment_id=str(enrollment.id)).order_by("occurred_at")

    assert transition is not None
    assert transition.count() == 1
    assert transition[0].action == "SUSPEND"
    assert transition[0].from_state == "active"
    assert transition[0].to_state == "suspended"
    assert transition[0].actor_id is not None
    assert transition[0].occurred_at is not None
    assert transition[0].justification == "justification"
    assert transition[0].created_at is not None
    assert transition[0].transition_id is not None





    








            



