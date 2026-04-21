from datetime import UTC, date, datetime

import pytest

from domain.identity.user.entities.user import User
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from domain.identity.user.value_objects.user_state import UserState


@pytest.fixture
def make_user():
    def _make(*, state):

        now = datetime.now(UTC)

        created_at = now 
        activated_at = now if state == UserState.ACTIVE else None
        suspended_at = now if state == UserState.SUSPENDED else None
        inactivated_at = now if state == UserState.INACTIVE else None

        return User(
            id="user1_id",
            legal_identity=LegalIdentity(
                identity_type=LegalIdentityType.CPF,
                identity_number="12345678912",
                identity_issuer="PB"
            ),
            full_name="user-id-1",
            birth_date=date(1990, 1, 1),
            created_by="actor-1",
            email="exemple1@email.com",
            guardian_id="guardian-id-1",
            state=state,
            created_at=created_at,
            activated_at=activated_at,
            suspended_at=suspended_at,
            inactivated_at=inactivated_at
        )
    return _make
