from datetime import UTC, date, datetime

from domain.identity.user.entities.user import User
from domain.identity.user.events.user_events import UserCreated
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from domain.identity.user.value_objects.user_state import UserState


def test_create_user_success():
    # Arrange
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
        occurred_at=datetime.now(UTC)
    
    )

    # Assert
    assert isinstance(user, User)
    assert user.state == UserState.PENDING
    assert user.activated_at is None
    assert user.suspended_at is None
    assert user.inactivated_at is None
    assert user.created_at is not None
    assert user.created_by == "actor-1"
    assert user.full_name == "user-1"
    assert user.birth_date == date(1990, 1, 1)

    assert user.email == "exemple1@email.com"
    assert len(user._domain_events) == 1
    assert len(user.transitions) == 0
    
    e = user._domain_events[-1]

    assert isinstance(e, UserCreated)
    assert e.aggregate_id == user.id
    assert e.actor_id == "actor-1"
    assert e.full_name == "user-1"
    assert e.birth_date == date(1990, 1, 1)
    assert e.occurred_at is not None
    assert e.occurred_at == user.created_at
    assert e.event_id is not None

def test_create_non_adult_user_success():
        # Arrange
    user = User.create(
        legal_identity=LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678912",
            identity_issuer="PB"
        ),
        full_name="user-1",
        birth_date=date(2020, 1, 1),
        created_by="actor-1",
        email="exemple1@email.com",
        occurred_at=datetime.now(UTC),
        guardian_id="guardian-1"
    
    )

    # Assert
    assert isinstance(user, User)
    assert user.state == UserState.PENDING
    assert user.activated_at is None
    assert user.suspended_at is None
    assert user.inactivated_at is None
    assert user.created_at is not None
    assert user.created_by == "actor-1"
    assert user.full_name == "user-1"
    assert user.birth_date == date(2020, 1, 1)
    assert user.guardian_id == "guardian-1"


    assert user.email == "exemple1@email.com"
    assert len(user._domain_events) == 1
    assert len(user.transitions) == 0
    
    e = user._domain_events[-1]

    assert isinstance(e, UserCreated)
    assert e.aggregate_id == user.id
    assert e.actor_id == "actor-1"
    assert e.full_name == "user-1"
    assert e.birth_date == date(2020, 1, 1)
    assert e.occurred_at is not None
    assert e.occurred_at == user.created_at
    assert e.event_id is not None
