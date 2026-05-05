from datetime import UTC, datetime

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.services.close_user import InactivateUserService
from domain.identity.user.events.user_events import UserInactivated
from domain.identity.user.value_objects.user_state import UserState
from tests.application.identity.user.fakes_user import (
    FailingUserRepository,
    InMemoryUserRepository,
    make_user,
)


def test_inactivate_user_success():
  
    # Arrange:
    repo = InMemoryUserRepository()
    user = make_user(state=UserState.PENDING)
    service = InactivateUserService(repo=repo)
    repo.save(user)
    repo.save_calls = 0

    result = service.execute(
        user_id=user.id,
        actor_id="user-1",
        justification="justification",
        occurred_at=datetime.now(UTC),
    )
    # Assert:
    assert result.success is True
    assert len(result.domain_events) == 1

    event = result.domain_events[0]
    assert isinstance(event, UserInactivated)

    assert result.changed is True
    assert result.aggregate_id == user.id

    assert result.new_state == UserState.INACTIVE
    assert event.from_state.value == UserState.PENDING.value
    assert event.to_state.value == UserState.INACTIVE.value

    assert repo.save_calls == 1

    persisted_user = repo.get_by_id(user.id)
    assert persisted_user is not None
    assert persisted_user.state == UserState.INACTIVE
    assert persisted_user.inactivated_at is not None


def test_inactivate_user_not_found():
    repo = InMemoryUserRepository()
    service = InactivateUserService(repo=repo)

    result = service.execute(
        user_id="user-missing",
        actor_id="user-1",
        justification="justification",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.domain_events == ()
    assert result.new_state is None
    assert result.error is not None
    assert result.error.code == ErrorCodes.USER_NOT_FOUND
    assert repo.save_calls == 0



def test_inactivate_user_returns_failure_when_save_fails():
    repo = FailingUserRepository(message="db down")
    user = make_user(state=UserState.ACTIVE)
    repo.seed(user)

    service = InactivateUserService(repo=repo)

    result = service.execute(
        user_id=user.id,
        actor_id="user-1",
        justification="justification",
        occurred_at=datetime.now(UTC),
    )

    assert result.success is False
    assert result.changed is False
    assert result.error is not None
    assert result.error.code == ErrorCodes.DATABASE_ERROR
    assert repo.save_calls == 1

    assert result.error.details["aggregate_id"] == user.id
    assert result.error.details["action"] == "inactivate"
    assert result.error.details["current_state"] == UserState.INACTIVE.value 


    

def test_inactivate_user_returns_failure_when_user_is_already_inactive():
    # Arrange:
    repo = InMemoryUserRepository()

    user = make_user(state=UserState.INACTIVE)
    repo.save(user)
    repo.save_calls = 0

    service = InactivateUserService(repo=repo)

    result = service.execute(
        user_id=user.id,
        actor_id="user-1",
        justification="justification",
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
    assert result.error.details["action"] == "inactivate"
    assert result.error.details["current_state"] == UserState.INACTIVE.value
