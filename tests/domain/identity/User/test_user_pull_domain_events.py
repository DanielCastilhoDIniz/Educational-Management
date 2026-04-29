from datetime import UTC, date, datetime

import pytest

from domain.identity.user.events.user_events import UserSuspended
from domain.identity.user.value_objects.user_state import UserState


def test_user_pull_domain_events(make_user):
    user = make_user(state=UserState.ACTIVE)

    events_before = len(user._domain_events)
  
    assert len(user.transitions) == 0

    assert len(user._domain_events) == 0
    events = user.pull_domain_events()
    assert len(events) == events_before
    assert events == []

    user.suspend(
        actor_id="actor-2",
        occurred_at=datetime.now(UTC),
        justification="Testing suspend"
    )
    assert len(user.transitions) == 1

    assert len(user._domain_events) == 1
    assert isinstance(user._domain_events[0], UserSuspended)
    assert user._domain_events[0].actor_id == "actor-2"
    assert user._domain_events[0].justification == "Testing suspend"
    assert user._domain_events[0].occurred_at is not None
    assert user._domain_events[0].event_id is not None
    assert user._domain_events[0].aggregate_id == user.id
    assert user.state == UserState.SUSPENDED
    assert user.suspended_at is not None

    events = user.pull_domain_events()
    assert len(user._domain_events) == 0
    assert len(events) == 1
    e = events[0]
    assert e.actor_id == "actor-2" 
    assert e.justification == "Testing suspend"
    assert e.occurred_at is not None    
    assert e.event_id is not None
    assert e.aggregate_id == user.id
    assert isinstance(e, UserSuspended)


def test_user_pull_domain_events_with_no_events(make_user):
    user = make_user(state=UserState.ACTIVE)
    state_before = user.state
    events_before = len(user._domain_events)
    transitions_before = len(user.transitions)

    assert len(user._domain_events) == 0
    events = user.pull_domain_events()
    assert len(events) == events_before
    assert events == []
    assert user.state == state_before
    assert len(user.transitions) == transitions_before


def test_user_peek_domain_events(make_user):
    user = make_user(state=UserState.ACTIVE)

    events_before = len(user._domain_events)
  
    assert len(user.transitions) == 0

    assert len(user._domain_events) == 0
    events = user.peek_domain_events()
    assert len(events) == events_before
    assert events == []

    user.suspend(
        actor_id="actor-2",
        occurred_at=datetime.now(UTC),
        justification="Testing suspend"
    )
    assert len(user.transitions) == 1

    assert len(user._domain_events) == 1
    assert isinstance(user._domain_events[0], UserSuspended)
    assert user._domain_events[0].actor_id == "actor-2"
    assert user._domain_events[0].justification == "Testing suspend"
    assert user._domain_events[0].occurred_at is not None
    assert user._domain_events[0].event_id is not None
    assert user._domain_events[0].aggregate_id == user.id
    assert user.state == UserState.SUSPENDED
    assert user.suspended_at is not None

    events = user.peek_domain_events()
    assert len(user._domain_events) == 1
    assert len(events) == 1
    e = events[0]
    assert e.actor_id == "actor-2" 
    assert e.justification == "Testing suspend"
    assert e.occurred_at is not None    
    assert e.event_id is not None
    assert e.aggregate_id == user.id
    assert isinstance(e, UserSuspended)