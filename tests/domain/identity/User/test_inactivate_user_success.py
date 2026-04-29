from datetime import UTC, date, datetime

from domain.identity.user.events.user_events import UserInactivated
from domain.identity.user.value_objects.user_state import UserState
from domain.identity.user.value_objects.user_transition import UserTransition


# ---------------------------------tests---------------------------------------
def test_inactivate_user_success_from_active(make_user):
    # Arrange
    user_1 = make_user(state=UserState.ACTIVE)

    #act
    user_1.inactivate(
        actor_id="actor_id_1",
        occurred_at=datetime.now(UTC),
        justification="Violation of terms of service"
    )

    assert str(user_1.state) == UserState.INACTIVE.value
    assert user_1.inactivated_at is not None
    assert len(user_1.transitions) == 1
    assert len(user_1._domain_events) == 1
    
    
    e = user_1._domain_events[-1]
    assert isinstance(e, UserInactivated)
    assert e.aggregate_id == user_1.id
    assert e.event_id is not None


    t = user_1.transitions[-1]
    assert isinstance(t, UserTransition)
    assert t.actor_id == "actor_id_1"
    assert str(t.from_state) == UserState.ACTIVE.value
    assert str(t.to_state) == UserState.INACTIVE.value
    assert t.justification == "Violation of terms of service"


def test_inactivate_user_success_from_suspended(make_user):
    # Arrange
    user_1 = make_user(state=UserState.SUSPENDED)

    #act
    user_1.inactivate(
        actor_id="actor_id_1",
        occurred_at=datetime.now(UTC),
        justification="Violation of terms of service"
    )

    assert str(user_1.state) == UserState.INACTIVE.value
    assert user_1.inactivated_at is not None
    assert len(user_1.transitions) == 1
    assert len(user_1._domain_events) == 1
    
    
    e = user_1._domain_events[-1]
    assert isinstance(e, UserInactivated)
    assert e.aggregate_id == user_1.id
    assert e.event_id is not None


    t = user_1.transitions[-1]
    assert isinstance(t, UserTransition)
    assert t.actor_id == "actor_id_1"
    assert str(t.from_state) == UserState.SUSPENDED.value
    assert str(t.to_state) == UserState.INACTIVE.value
    assert t.justification == "Violation of terms of service"



def test_inactivate_user_success_from_pending(make_user):
    # Arrange
    user_1 = make_user(state=UserState.PENDING)

    #act
    user_1.inactivate(
        actor_id="actor_id_1",
        occurred_at=datetime.now(UTC),
        justification="Violation of terms of service"
    )

    assert str(user_1.state) == UserState.INACTIVE.value
    assert user_1.inactivated_at is not None
    assert len(user_1.transitions) == 1
    assert len(user_1._domain_events) == 1
    
    
    e = user_1._domain_events[-1]
    assert isinstance(e, UserInactivated)
    assert e.aggregate_id == user_1.id
    assert e.event_id is not None


    t = user_1.transitions[-1]
    assert isinstance(t, UserTransition)
    assert t.actor_id == "actor_id_1"
    assert str(t.from_state) == UserState.PENDING.value
    assert str(t.to_state) == UserState.INACTIVE.value
    assert t.justification == "Violation of terms of service"
  