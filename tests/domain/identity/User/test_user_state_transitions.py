from datetime import UTC, datetime

import pytest

from domain.identity.user.value_objects.user_state import UserState
from domain.identity.user.value_objects.user_transition import UserTransition
from domain.shared.domain_error import DomainError


def test_rejects_none_occurred_at() -> None:
    with pytest.raises(DomainError) as exc_info:
        UserTransition(
            from_state=UserState.ACTIVE,
            actor_id="user-1",
            to_state=UserState.SUSPENDED,
            occurred_at=None, # type: ignore
        )
    

    err = exc_info.value
    assert err.code == "invalid_occurred_at"
    assert err.message == "occurred_at cannot be None"
    assert err.details is not None
    assert err.details["occurred_at"] is None

def test_rejects_empty_actor_id() -> None:
    with pytest.raises(DomainError) as exc_info:
        UserTransition(
            from_state=UserState.ACTIVE,
            actor_id="   ",
            to_state=UserState.SUSPENDED,
            occurred_at=datetime.now(UTC),
        )

    err = exc_info.value
    assert err.code == "invalid_actor_id"
    assert err.message == "actor_id cannot be empty"
    assert err.details is not None
    assert err.details["actor_id"] == "   "


def test_normalizes_naive_occurred_at_to_utc() -> None:
    occurred_at = datetime(2026, 1, 15, 10, 30, 0)

    transition = UserTransition(
        from_state=UserState.ACTIVE,
        actor_id="user-1",
        to_state=UserState.SUSPENDED,
        occurred_at=occurred_at,
    )

    assert transition.occurred_at.tzinfo == UTC
    assert transition.occurred_at == occurred_at.replace(tzinfo=UTC)


def test_rejects_same_from_and_to_state() -> None:
    with pytest.raises(DomainError) as exc_info:
        UserTransition(
            from_state=UserState.ACTIVE,
            actor_id="user-1",
            to_state=UserState.ACTIVE,
            occurred_at=datetime.now(UTC),
        )

    err = exc_info.value
    assert err.code == "invalid_state_transition"
    assert err.message == "from_state and to_state cannot be the same"
    assert err.details is not None
    assert err.details["from_state"] == UserState.ACTIVE
    assert err.details["to_state"] == UserState.ACTIVE


def test_valid_state_transition() -> None:
    occurred_at = datetime(2026, 1, 15, 10, 30, 0)

    transition = UserTransition(
        from_state=UserState.ACTIVE,
        actor_id="user-1",
        to_state=UserState.SUSPENDED,
        occurred_at=occurred_at,
        justification="Testing valid transition"
    )

    assert transition.from_state == UserState.ACTIVE
    assert transition.to_state == UserState.SUSPENDED
    assert transition.actor_id == "user-1"
    assert transition.occurred_at == occurred_at.replace(tzinfo=UTC)
    assert transition.justification == "Testing valid transition"


@pytest.mark.parametrize(
    "state, command, expected_code",
    [
      (UserState.PENDING, lambda u: u.suspend(actor_id="admin-1", justification="Violation of terms"), "invalid_state_transition"),
        (UserState.ACTIVE, lambda u:u.activate(actor_id="admin-1"), "invalid_state_transition"),
        (UserState.SUSPENDED, lambda u:u.suspend(actor_id="admin-1", justification="Repeated violation"), "invalid_state_transition"),
    
    ])

def test_forbidden_transitions(make_user, state, command, expected_code):
    user = make_user(state=state)
    with pytest.raises(DomainError) as exc_info:
        command(user)
    assert exc_info.value.code == expected_code

   
def test_raises_invalid_state_transition(make_user) -> None:
    user  = make_user(state=UserState.PENDING)

    
    with pytest.raises(DomainError) as exc_info:
        user.suspend(
            actor_id="admin-1",
            justification="Violation of terms")

    err = exc_info.value
    assert err.code == "invalid_state_transition"
    assert err.message == "Cannot transition from pending to suspended."
    assert err.details is not None