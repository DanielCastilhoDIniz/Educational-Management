from datetime import UTC, date, datetime, timedelta

import pytest

from domain.identity.user.entities.user import User
from domain.identity.user.errors.user_errors import UserRequiredGuardianIDError
from domain.identity.user.events.user_events import UserCreated
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from domain.identity.user.value_objects.user_state import UserState
from domain.shared.domain_error import DomainError

# ---------------------------------tests---------------------------------------

def make_valid_kwargs():
    fields = {
            "identity_type": LegalIdentityType.CPF,
            "identity_number":"12345678912",
            "identity_issuer": "PB"

    }
    return fields

@pytest.mark.parametrize(
    "field, value, expected_code",
    [
        
        ("identity_type", None, "invalid_identity_type"),
        ("identity_number", None, "invalid_identity_number"),
        ("identity_number", "", "invalid_identity_number"),
        ("identity_number", "  ", "invalid_identity_number"),
        ("identity_issuer", None, "invalid_identity_issuer"),
        ("identity_issuer", "", "invalid_identity_issuer"),
        ("identity_issuer", " ", "invalid_identity_issuer"),
    ]
)

def test_validate_legal_identity_fields(field, value, expected_code):
    kwargs = make_valid_kwargs()
    kwargs[field] = value

    with pytest.raises(DomainError) as exc_info:
        LegalIdentity(**kwargs)
        

    err = exc_info.value
    assert err.code == expected_code
# ----------------------------------------------------------------------------------------