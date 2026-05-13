
import uuid
from datetime import date

from apps.identity.mappers.user_mapper import UserMapper
from apps.identity.models.user_model import UserModel

from domain.identity.user.entities.user import User
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType


def test_roundtrip_to_snapshot_return_orm():
    user = User.create(
        legal_identity=LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678910",
            identity_issuer="Issuer",
        ),
        full_name="John Doe",
        birth_date=date(1980, 1, 1),
        created_by="user123",
        email="example@email.com",   
   )
    
    snapshot = UserMapper.to_snapshot(user=user)

    assert isinstance(snapshot, UserModel)
    assert snapshot.id == user.id
    assert snapshot.full_name == user.full_name
    assert snapshot.email == user.email
    assert snapshot.birth_date == user.birth_date
    assert snapshot.created_by == user.created_by
    assert snapshot.guardian_id == user.guardian_id
    assert snapshot.state == user.state.value
    assert snapshot.created_at == user.created_at
    assert snapshot.identity_type == user.legal_identity.identity_type.value
    assert snapshot.identity_number == user.legal_identity.identity_number
    assert snapshot.identity_issuer == user.legal_identity.identity_issuer

 
def test_roundtrip_to_snapshot_and_to_domain():
    user = User.create(
        legal_identity=LegalIdentity(
            identity_type=LegalIdentityType.CPF,
            identity_number="12345678910",
            identity_issuer="Issuer",
        ),
        full_name="John Doe",
        birth_date=date(1980, 1, 1),
        created_by="user123",
        email="example@email.com",   
   )

    snapshot = UserMapper.to_snapshot(user=user)
    domain = UserMapper.to_domain(snapshot=snapshot, transitions=[])

    assert isinstance(domain, User)
    assert domain.id == user.id
    assert domain.full_name == user.full_name
    assert domain.email == user.email
    assert domain.birth_date == user.birth_date
    assert domain.created_by == user.created_by
    assert domain.guardian_id == user.guardian_id
    assert domain.state == user.state
    assert domain.created_at == user.created_at
    assert domain.legal_identity.identity_type == user.legal_identity.identity_type
    assert domain.legal_identity.identity_number == user.legal_identity.identity_number
    assert domain.legal_identity.identity_issuer == user.legal_identity.identity_issuer

    assert domain.version == user.version
    assert domain.transitions == []



