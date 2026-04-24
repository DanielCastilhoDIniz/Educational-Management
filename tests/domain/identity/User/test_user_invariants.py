from datetime import UTC, date, datetime, timedelta

import pytest

from domain.identity.user.entities.user import User
from domain.identity.user.errors.user_errors import UserRequiredGuardianIDError
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from domain.identity.user.value_objects.user_state import UserState
from domain.shared.domain_error import DomainError

# ---------------------------------tests---------------------------------------

def test_create_user_raises_error_for_user_minors_without_guardian():
      
    with pytest.raises(UserRequiredGuardianIDError) as exc_info:
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
            occurred_at=datetime.now(UTC)        
        )
    
    err = exc_info.value
    assert err.code == "user_requires_guardian"
    assert err.message == "User under 18 years old must have a guardian_id."
    assert err.details == {"birth_date": "2020-01-01"}


# -------------------------------validate fields -------------------------------
def make_valid_kwargs():
    fields = {
        "legal_identity": LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678912",
            identity_issuer="PB"
        ),
        "full_name": "user-1",
        "birth_date": date(1990, 1, 1), 
        "created_by": "actor-1",
        "email": "exemple1@email.com",
        "occurred_at": datetime.now(UTC),
        "guardian_id": "guardian-1",
    }
    return fields

@pytest.mark.parametrize(
    "field, value, expected_code",
    [
        ("full_name", "", "invalid_full_name"),
        ("full_name", None, "invalid_full_name"),
        ("full_name", " ", "invalid_full_name"),
        ("full_name", "\t", "invalid_full_name"),
        ("created_by", "", "invalid_created_by"),
        ("created_by", None, "invalid_created_by"),
        ("created_by"," ", "invalid_created_by"),
        ("created_by", "\t", "invalid_created_by"),
        ("email", "", "invalid_email"),
        ("email", " ", "invalid_email"),
        ("email", "\t", "invalid_email"),
        ("birth_date", None, "invalid_birth_date"),
        ("birth_date",(date.today() + timedelta(days=1)), "invalid_birth_date"),
        ("legal_identity", None, "invalid_legal_identity"),
    ])

def test_validate_fields_full_name_create_by_email(field, value, expected_code):
    kwargs = make_valid_kwargs()
    kwargs[field] = value

    with pytest.raises(DomainError) as exc_info:
        User.create(**kwargs)

    err = exc_info.value
    assert err.code == expected_code
# ----------------------------------------------------------------------------------------






    



