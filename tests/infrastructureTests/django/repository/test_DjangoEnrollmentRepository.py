import uuid
from datetime import UTC, datetime

import pytest
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel
from apps.academic.repositories.django_enrollment_repository import DjangoEnrollmentRepository

from application.academic.enrollment.errors.persistence_errors import (
    ConcurrencyConflictError,
)
from infrastructure.django.apps.academic.enrollments.transition_id import (
    make_transition_id,
)
from infrastructure.errors.persistence_errors import InfrastructureError
from infrastructureTests.factory.new_enrollment_factory import (
    factory_create_new_enrollment_for_tests,
)


@pytest.mark.django_db(transaction=True)
def test_get_by_id_snapshot_is_none_when_enrollment_does_not_exist() -> None:
    repository = DjangoEnrollmentRepository()
    result = repository.get_by_id(str(uuid.uuid4()))
    assert result is None


@pytest.mark.django_db(transaction=True)
def test_get_by_id_success() -> None:

    enrollment = factory_create_new_enrollment_for_tests()
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
def test_save_return_concurrency_conflict_error() -> None:
    enrollment = factory_create_new_enrollment_for_tests()
    repository = DjangoEnrollmentRepository()
    result_one = repository.get_by_id(enrollment_id=str(enrollment.id))

    assert result_one is not None

    result_one.suspend(actor_id="actor-1", justification="justification", occurred_at=datetime.now(UTC))  
  
    result_two = EnrollmentModel.objects.get(id=str(enrollment.id))
    result_two.version += 1
    result_two.save()
    
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
    enrollment = factory_create_new_enrollment_for_tests()
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
    assert enrollment_before.reactivated_at is None
    assert enrollment_before.updated_at is not None

    assert new_version == enrollment_before.version + 1
    assert enrollment_after.version == enrollment_before.version +1
    assert enrollment_after.state == "suspended"
    assert enrollment_after.suspended_at is not None
    assert enrollment_after.concluded_at is None
    assert enrollment_after.cancelled_at is None
    assert enrollment_after.reactivated_at is None
    assert enrollment_after.updated_at is not None
    assert enrollment_after.created_at == enrollment_before.created_at
    assert enrollment_after.student_id == enrollment_before.student_id
    assert enrollment_after.class_group_id == enrollment_before.class_group_id
    assert enrollment_after.academic_period_id == enrollment_before.academic_period_id
    assert enrollment_after.id == enrollment_before.id

    transition = EnrollmentTransitionModel.objects.filter(enrollment_id=str(enrollment.id)).order_by("occurred_at")

    assert transition is not None
    assert transition.count() == 1
    assert transition[0].action == "suspend"
    assert transition[0].from_state == "active"
    assert transition[0].to_state == "suspended"
    assert transition[0].actor_id is not None
    assert transition[0].occurred_at is not None
    assert transition[0].justification == "justification"
    assert transition[0].created_at is not None
    assert transition[0].transition_id is not None

@pytest.mark.django_db(transaction=True)
def test_no_op_dont_create_transition():
    enrollment = factory_create_new_enrollment_for_tests(state="cancelled",cancelled_at=datetime(2023, 1, 1, tzinfo=UTC))
    repository = DjangoEnrollmentRepository()
    result = repository.get_by_id(enrollment_id=str(enrollment.id))

    assert result is not None

    line_before = len(result.transitions)

    result.cancel(actor_id=str(uuid.uuid4()), occurred_at=datetime.now(UTC), justification="justification")

    assert len(result.transitions) ==  line_before


@pytest.mark.django_db(transaction=True)
def test_retry_should_not_create_transition():
    # ARRANGE
    # 1. Initialize the repository and create the initial domain entity
    repository = DjangoEnrollmentRepository()
    enrollment = factory_create_new_enrollment_for_tests()

    # 2. Retrieve the aggregate to ensure it is correctly loaded
    result = repository.get_by_id(enrollment_id=str(enrollment.id))
    assert result is not None

    # 3. Prepare the data for the suspension transition
    actor_id = str(uuid.uuid4())
    justification = "Testing idempotency"
    occurred_at = datetime.now(UTC)

    # ACT
    # 4. Trigger the business rule in the domain entity
    result.suspend(actor_id=actor_id, justification=justification, occurred_at=occurred_at)
    initial_transitions_count = len(result.transitions)
    
    # 5. First persistence attempt (Expected success)
    first_version = repository.save(result)
    
    # 6. Second persistence attempt (Simulating a Retry/Idempotency scenario)
    # The repository should hit the `updated_rows == 0` block and validate the snapshot
    retry_version = repository.save(result)

    # ASSERT
    # 7. Validate version consistency and memory state
    assert first_version == enrollment.version + 1
    assert retry_version == first_version
    assert len(result.transitions) == initial_transitions_count

    # 8. Database Persistence Validations (Direct DB queries)
    enrollment_db = EnrollmentModel.objects.get(id=str(enrollment.id))
    transitions_db = EnrollmentTransitionModel.objects.filter(enrollment_id=str(enrollment.id))

    assert enrollment_db.version == first_version
    assert enrollment_db.state == "suspended"  # Verify if your DB stores lowercase or uppercase
    
    # CRITICAL ASSERT: The count must remain 1, proving the retry did not duplicate the record
    assert transitions_db.count() == 1
    assert EnrollmentTransitionModel.objects.count() == 1

@pytest.mark.django_db(transaction=True)
def test_bd_remains_consistent_when_transition_fails_to_save():
     
    # ARRANGE
    # 1. Initialize the repository and create the initial domain entity
    repository = DjangoEnrollmentRepository()
    enrollment = factory_create_new_enrollment_for_tests()

    # 2. Retrieve the aggregate to ensure it is correctly loaded
    result = repository.get_by_id(enrollment_id=str(enrollment.id))
    assert result is not None

    # 3. retrieve snapshot

    origin_id = enrollment.id
    origin_version = enrollment.version
    origin_state = enrollment.state

    # 4. Prepare the data for the suspension transition
    actor_id = str(uuid.uuid4())
    justification = "Testing idempotency"
    occurred_at = datetime.now(UTC)

    # ACT
    # 4. Trigger the business rule in the domain entity
    result.suspend(actor_id=actor_id, justification=justification, occurred_at=occurred_at)

    transition_expected = make_transition_id(
         enrollment_id=origin_id,
         action="suspend",
         from_state=origin_state,
         to_state="suspended",
         occurred_at=occurred_at,
         actor_id=actor_id,
         justification=justification,         
    )

    new_transition =EnrollmentTransitionModel.objects.create(  # noqa: F841
        transition_id=transition_expected,
        enrollment_id=origin_id,
        action="suspend",
        from_state=origin_state,
        to_state="suspended",
        actor_id=actor_id,
        occurred_at=occurred_at,
        justification=justification,
    )
       
    with pytest.raises(InfrastructureError) as e:
        repository.save(result)

    assert e.value.code == "database_error"
    assert e.value.message == "A critical error occurred on the database server."
    assert e.value.details is not None

    query1 = EnrollmentModel.objects.get(id=str(enrollment.id))
    assert query1.version == origin_version
    assert query1.state == origin_state

    query2 = EnrollmentTransitionModel.objects.filter(enrollment_id=str(origin_id)).count()
    assert query2 == 1

@pytest.mark.django_db(transaction=True)
def test_snapshot_and_transition_ensure_safe_rehydration():
    # Arrange 1:
    enrollment = factory_create_new_enrollment_for_tests()
    repository = DjangoEnrollmentRepository()

    result = repository.get_by_id(enrollment_id=str(enrollment.id))
    assert result is not None

    # retrieve snapshot
    origin_id = enrollment.id
     
    # Prepare the data for the reactivate transition
    actor_id = str(uuid.uuid4())
    justification = "justification"
    occurred_at_fake = datetime(2026, 1, 2, tzinfo=UTC) 
    
    #Act 1:
    result.suspend(actor_id=actor_id, justification=justification, occurred_at=occurred_at_fake)
    repository.save(result)

    # Arrange 2:
    state_suspended = (EnrollmentModel.objects.get(id=str(enrollment.id))).state
     
    transition_id_before = make_transition_id(
         enrollment_id=origin_id,
         action="reactivate",
         from_state=state_suspended,
         to_state="active",
         occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
         actor_id=actor_id,
         justification=justification,         
    )

    new_transition =EnrollmentTransitionModel.objects.create(
        transition_id=transition_id_before,
        enrollment_id=origin_id,
        action="reactivate",
        from_state=state_suspended,
        to_state="active",
        actor_id=actor_id,
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
        justification=justification,
    )

    result_reactivated = repository.get_by_id(enrollment_id=str(enrollment.id))
    assert result_reactivated is not None

    # Asserts:
    assert result_reactivated.transitions[0].occurred_at == new_transition.occurred_at
    assert result_reactivated.transitions[1].occurred_at == occurred_at_fake
    count_transitions = EnrollmentTransitionModel.objects.filter(enrollment_id=str(enrollment.id)).count()
    assert count_transitions == 2
    

  




   




   


