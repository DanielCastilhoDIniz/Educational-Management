from datetime import UTC, datetime

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.services.activate_user import ActivateUserService
from domain.identity.user.events.user_events import UserActivated
from domain.identity.user.value_objects.user_state import UserState
from tests.application.identity.user.fakes_user import (
    FailingUserRepository,
    InMemoryUserRepository,
    make_user,
)


def test_activate_user_success():
    # Arrange:
    repo = InMemoryUserRepository()
    user = make_user(state=UserState.PENDING)
    service = ActivateUserService(repo=repo)
    repo.save(user)
    repo.save_calls = 0
    # Act:

    result = service.execute(
        user_id=user.id,
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
    )
    # Assert:
    assert result.success is True
    assert len(result.domain_events) == 1

    event = result.domain_events[0]
    assert isinstance(event, UserActivated)

    assert result.changed is True
    assert result.aggregate_id == user.id

    assert result.new_state == UserState.ACTIVE
    assert event.from_state.value == UserState.PENDING.value
    assert event.to_state.value == UserState.ACTIVE.value

    assert repo.save_calls == 1

    persisted_user = repo.get_by_id(user.id)
    assert persisted_user is not None
    assert persisted_user.state == UserState.ACTIVE
    assert persisted_user.activated_at is not None


def test_activate_user_not_found():
    repo = InMemoryUserRepository()
    service = ActivateUserService(repo=repo)
    
    result = service.execute(
        user_id="user-missing",
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.USER_NOT_FOUND
    assert repo.save_calls == 0

def test_activate_user_returns_failure_when_user_is_not_pending():
    # Arrange:
    repo = InMemoryUserRepository()

    user = make_user(state=UserState.ACTIVE)
    repo.save(user)
    repo.save_calls = 0
  
    service = ActivateUserService(repo=repo)
    # Act:

    result = service.execute(
        user_id=user.id,
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert repo.save_calls == 0

    assert result.error is not None
    assert result.error.code == ErrorCodes.INVALID_STATE_TRANSITION
    assert result.error.details is not None
    assert result.error.details["aggregate_id"] == user.id
    assert result.error.details["action"] == "activate"
    assert result.error.details["current_state"] == UserState.ACTIVE.value

def test_activate_user_returns_failure_when_save_fails():
    repo = FailingUserRepository(message="db down")
    user = make_user(state=UserState.PENDING)
    repo.seed(user)

    service = ActivateUserService(repo=repo)

    result = service.execute(
        user_id=user.id,
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.error is not None
    assert result.error.code == ErrorCodes.DATABASE_ERROR
    assert repo.save_calls == 1
    

