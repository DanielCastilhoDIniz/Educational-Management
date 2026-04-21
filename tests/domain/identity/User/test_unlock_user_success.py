from datetime import UTC, date, datetime

from domain.identity.user.events.user_events import UserUnlocked
from domain.identity.user.value_objects.user_state import UserState
from domain.identity.user.value_objects.user_transition import UserTransition


# ---------------------------------tests---------------------------------------
def test_unlock_user_success(make_user):
    # Arrange
    user_1 = make_user(state=UserState.SUSPENDED)

    #act
    user_1.unlock(
        actor_id="actor_id_1",
        occurred_at=datetime.now(UTC),
        justification="Rehabilitation after suspension"
    )

    assert str(user_1.state) == UserState.ACTIVE.value
    assert user_1.unlocked_at is not None
    assert len(user_1.transitions) == 1
    assert len(user_1._domain_events) == 1
    
    
    e = user_1._domain_events[-1]
    assert isinstance(e, UserUnlocked)
    assert e.aggregate_id == user_1.id
    assert e.event_id is not None


    t = user_1.transitions[-1]
    assert isinstance(t, UserTransition)
    assert t.actor_id == "actor_id_1"
    assert str(t.from_state) == UserState.SUSPENDED.value
    assert str(t.to_state) == UserState.ACTIVE.value
    assert t.justification == "Rehabilitation after suspension"
  