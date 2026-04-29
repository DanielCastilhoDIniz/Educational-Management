from dataclasses import fields
from datetime import UTC, date, datetime, timedelta

import pytest

from domain.identity.user.entities.user import User
from domain.identity.user.errors.user_errors import UserRequiredGuardianIDError
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from domain.identity.user.value_objects.user_state import UserState
from domain.shared.domain_error import DomainError
from domain.identity.user.errors.user_errors import JustificationRequiredError


# ---------------------------------helper---------------------------------------

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


def make_valid_rehydrate_kwargs():
        fields = {
            "id": "user-1",
            "state": UserState.ACTIVE,
            "legal_identity": LegalIdentity(
                identity_type=LegalIdentityType.CPF,
                identity_number="12345678912",
                identity_issuer="PB"
            ),
            "full_name": "user-1",
            "birth_date": date(1990, 1, 1), 
            "created_by": "actor-1",
            "email": "exemple1@email.com",
            "created_at": datetime.now(UTC),
            "guardian_id": "guardian-1",
            "activated_at": datetime.now(UTC),


        }
        return fields


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


def test_validate_rehydrate_without_activated_at_raises_domain_error():
    kwargs = make_valid_rehydrate_kwargs()
    kwargs.pop("activated_at")

    with pytest.raises(DomainError) as exc_info:
        User(**kwargs)
    err = exc_info.value
    assert err.code == "missing_activated_at"
    assert err.message == "User in state active requires field activated_at."

def test_validate_rehydrate_without_suspended_at_raises_domain_error():
    kwargs = make_valid_rehydrate_kwargs()
    kwargs["state"] = UserState.SUSPENDED


    with pytest.raises(DomainError) as exc_info:
        User(**kwargs)
    err = exc_info.value
    assert err.code == "missing_suspended_at"
    assert err.message == "User in state suspended requires field suspended_at."


def test_validate_rehydrate_without_inactivated_at_raises_domain_error():
    kwargs = make_valid_rehydrate_kwargs()
    kwargs["state"] = UserState.INACTIVE


    with pytest.raises(DomainError) as exc_info:
        User(**kwargs)
    err = exc_info.value
    assert err.code == "missing_inactivated_at"
    assert err.message == "User in state inactive requires field inactivated_at."


#-----------------required fields for states - justification-----------------
@pytest.mark.parametrize(
    "state,command,expected_code",
    [
        
        (UserState.SUSPENDED, lambda u:u.unlock(actor_id="admin-1", justification=""), "justification_required"),
        (UserState.SUSPENDED, lambda u:u.unlock(actor_id="admin-1", justification="  "), "justification_required"),
        
        (UserState.ACTIVE, lambda u:u.suspend(actor_id="admin-1", justification=""), "justification_required"),
        (UserState.ACTIVE, lambda u:u.suspend(actor_id="admin-1", justification="  "), "justification_required"),
        
        (UserState.ACTIVE, lambda u:u.inactivate(actor_id="admin-1", justification=""), "justification_required"),
        (UserState.ACTIVE, lambda u:u.inactivate(actor_id="admin-1", justification="  "), "justification_required"),
    ])
def test_validate_justification_required_for_state_transitions(make_user, state, command, expected_code):
    user = make_user(state=state)
    with pytest.raises(JustificationRequiredError) as exc_info:
        command(user)
    assert exc_info.value.code == expected_code
