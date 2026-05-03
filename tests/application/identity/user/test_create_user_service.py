from datetime import UTC, date, datetime

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.services.create_user import CreateUser
from domain.identity.user.events.user_events import UserCreated
from domain.identity.user.value_objects.user_state import UserState
from tests.application.identity.user.fakes_user import (
    FailingUserRepository,
    InMemoryUserRepository,
)


def test_create_user_success() -> None:
    # arrange:
    repo = InMemoryUserRepository()
    service = CreateUser(repo=repo)

    # Act:
    user = service.execute(
        identity_type="cpf",
        identity_number="12345678901",
        identity_issuer="SSD",
        full_name="John Doe",
        birth_date=date(1990, 1, 1),
        email="example@email.com",
        created_by="actor-1",
        occurred_at=datetime.now(UTC)
    )

    # Assert:
    assert user is not None
    assert user.success is True
    assert user.new_state is not None
    assert user.new_state == "pending"
    assert user.domain_events[0].__class__== UserCreated
    assert user.domain_events[0].aggregate_id == user.aggregate_id


def test_create_user_duplicate() -> None:
    # arrange:
    repo = InMemoryUserRepository()
    service = CreateUser(repo=repo)

    # Act 1:
    user = service.execute(
        identity_type="cpf",
        identity_number="12345678901",
        identity_issuer="SSD",
        full_name="John Doe",
        birth_date=date(1990, 1, 1),
        email="example@email.com",
        created_by="actor-1",
        occurred_at=datetime.now(UTC)
    )
    assert user is not None
    assert user.success is True
    assert user.new_state is not None
    assert user.new_state == "pending"

    # Act 2:
    user = service.execute(
        identity_type="cpf",
        identity_number="12345678901",
        identity_issuer="SSD",
        full_name="John Doe",
        birth_date=date(1990, 1, 1),
        email="example@email.com",
        created_by="actor-1",
        occurred_at=datetime.now(UTC)
    )

    assert user is not None
    assert user.success is False
    assert user.error is not None
    assert user.error.code == ErrorCodes.DUPLICATE_USER

def test_create_user_infrastructure_failure() -> None:
    # Arrange: 
    repo = FailingUserRepository(message="Failed to create user due to an infrastructure error.")
    service = CreateUser(repo=repo)

    # Act:
    user = service.execute(
        identity_type="cpf",
        identity_number="12345678901",
        identity_issuer="SSD",
        full_name="John Doe",
        birth_date=date(1990, 1, 1),
        email="example@email.com",
        created_by="actor-1",
        occurred_at=datetime.now(UTC)
    )

    # Assert:
    assert user is not None
    assert user.success is False
    assert user.error is not None
    assert user.error.code == ErrorCodes.USER_CREATION_FAILED





  
