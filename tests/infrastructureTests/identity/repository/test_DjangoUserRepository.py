import uuid
from datetime import UTC, date, datetime

import pytest
from apps.identity.models.user_model import UserModel
from apps.identity.models.user_transition_model import UserTransitionModel
from apps.identity.repositories.django_user_repository import DjangoUserRepository

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.errors.persistence_errors import (
    ConcurrencyConflictError,
    UserDuplicationError,
    UserPersistenceNotFoundError,
    UserTechnicalPersistenceError,
)
from domain.identity.user.entities.user import User
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from infrastructureTests.identity.factory.new_user_factory import factory_create_user_for_tests


@pytest.mark.django_db(transaction=True)
def test_get_by_id_snapshot_is_none_when_user_does_not_exist() -> None:

    # Arrange:
    repository = DjangoUserRepository()
    result = repository.get_by_id(str(uuid.uuid4()))
    assert result is None


@pytest.mark.django_db(transaction=True)
def test_get_by_id_success() -> None:
    user  =  factory_create_user_for_tests()
    repository = DjangoUserRepository()
    
    result = repository.get_by_id(user_id=str(user.id))
    
    assert result is not None
    assert result.id == str(user.id)
    assert result.legal_identity.identity_type == user.identity_type
    assert result.legal_identity.identity_number == user.identity_number
    assert result.legal_identity.identity_issuer == user.identity_issuer
    assert result.full_name == user.full_name
    assert result.birth_date == user.birth_date
    assert result.created_at == user.created_at
    assert result.state.value == user.state
    assert result.guardian_id == user.guardian_id


@pytest.mark.django_db(transaction=True)
def test_save_success() -> None:
    # Arrange:
    user = factory_create_user_for_tests()
    repository = DjangoUserRepository()
    result_before = repository.get_by_id(user_id=str(user.id))
    user_before = UserModel.objects.get(id=str(user.id))

    assert result_before is not None

    result_before.suspend(actor_id=str(uuid.uuid4()), occurred_at=datetime.now(UTC), justification="justification")
    
    new_version = repository.save(result_before)


    user_after = UserModel.objects.get(id=str(user.id))

    assert user_before.state == "active"
    assert user_before.suspended_at is None
    assert user_before.inactivated_at is None
    assert user_before.unlocked_at is None
    assert user_before.updated_at is not None

    assert new_version == user_before.version + 1
    assert user_after.version == user_before.version +1
    assert user_after.state == "suspended"
    assert user_after.suspended_at is not None
    assert user_after.inactivated_at is None
    assert user_after.unlocked_at is None
    assert user_after.updated_at is not None
    assert user_after.created_at == user_before.created_at
    assert user_after.id == user_before.id 
    assert user_after.full_name == user_before.full_name
    assert user_after.email == user_before.email
    assert user_after.guardian_id == user_before.guardian_id
    assert user_after.identity_type == user_before.identity_type
    assert user_after.identity_number == user_before.identity_number
    assert user_after.identity_issuer == user_before.identity_issuer

    transition = UserTransitionModel.objects.filter(user_id=str(user.id)).order_by("occurred_at")

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
def test_create_user_success() -> None:
    # Arrange:
    user = User.create(
        legal_identity=LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678912",
            identity_issuer="PB"
        ),
        full_name="user-1",
        birth_date=date(1990, 1, 1),
        created_by="actor-1",
        email="exemple1@email.com",
        occurred_at=datetime.now(UTC),
   
    )

    # Act:
    repository = DjangoUserRepository()
    version = repository.create(user)

    user_created = UserModel.objects.get(id=str(user.id))

    # Assert 
    assert user_created is not None
    assert user_created.state == "pending"
    assert user.full_name == user_created.full_name
    assert user.email == user_created.email
    assert user.birth_date == user_created.birth_date
    assert user.guardian_id == user_created.guardian_id

    assert user.created_by == user_created.created_by
    assert user_created.created_at is not None

    assert user.legal_identity.identity_type == user_created.identity_type
    assert user.legal_identity.identity_number == user_created.identity_number
    assert user.legal_identity.identity_issuer == user_created.identity_issuer

    assert user_created.id is not None
    assert user_created.version == version
    assert user_created.version == 1

    assert user_created.activated_at is None
    assert user_created.inactivated_at is None
    assert user_created.suspended_at is None

@pytest.mark.django_db(transaction=True)
def test_create_raises_duplication_error() -> None:
    # Arrange:
    user = User.create(
        legal_identity=LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678912",
            identity_issuer="PB"
        ),
        full_name="user-1",
        birth_date=date(1990, 1, 1),
        created_by="actor-1",
        email="exemple1@email.com",
        occurred_at=datetime.now(UTC),
    )

    # Act:
    repository = DjangoUserRepository()
    origin_version = repository.create(user)

    with pytest.raises(UserDuplicationError) as e:
        repository.create(user)

    # Asserts:
    assert e.value.code == ErrorCodes.DUPLICATE_USER
    assert e.value.message == "A user with the same identifiers already exists."
    assert e.value.details is not None

@pytest.mark.django_db(transaction=True)
def test_create_user_raises_duplication_error_on_duplicate_email() -> None:
    # Arrange 1:
    user = User.create(
        legal_identity=LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678912",
            identity_issuer="PB"
        ),
        full_name="user-1",
        birth_date=date(1990, 1, 1),
        created_by="actor-1",
        email="exemple1@email.com",
        occurred_at=datetime.now(UTC),
    )

    # Act:
    repository = DjangoUserRepository()
    repository.create(user)

    # Arrange 2:
    user_2 = User.create(
    legal_identity=LegalIdentity(
        identity_type=LegalIdentityType.CPF,
        identity_number="12345678910",
        identity_issuer="PB"
    ),
    full_name="user-1",
    birth_date=date(1990, 1, 1),
    created_by="actor-1",
    email="exemple1@email.com",
    occurred_at=datetime.now(UTC),
)

    with pytest.raises(UserDuplicationError) as e:
        repository.create(user_2)
    
    assert e.value.code == ErrorCodes.DUPLICATE_EMAIL
    assert e.value.message == "A user with the same email already exists."
    assert e.value.details is not None

@pytest.mark.django_db(transaction=True)
def test_create_user_raises_duplication_error_on_duplicate_identity() -> None:
    # Arrange 1:
    user = User.create(
        legal_identity=LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678912",
            identity_issuer="PB"
        ),
        full_name="user-1",
        birth_date=date(1990, 1, 1),
        created_by="actor-1",
        email="exemple1@email.com",
        occurred_at=datetime.now(UTC),
    )

    # Act:
    repository = DjangoUserRepository()
    repository.create(user)

    # Arrange 2:
    user_2 = User.create(
    legal_identity=LegalIdentity(
        identity_type=LegalIdentityType.CPF,
        identity_number="12345678912",
        identity_issuer="PB"
    ),
    full_name="user-1",
    birth_date=date(1990, 1, 1),
    created_by="actor-1",
    email="exemple2@email.com",
    occurred_at=datetime.now(UTC),
)

    with pytest.raises(UserDuplicationError) as e:
        repository.create(user_2)

    assert e.value.code == ErrorCodes.DUPLICATE_USER
    assert e.value.message == "A user with the same identifiers already exists."
    assert e.value.details is not None
