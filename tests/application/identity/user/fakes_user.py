from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Protocol, cast

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.errors.persistence_errors import (
    UserDuplicationError,
    UserTechnicalPersistenceError,
)
from domain.identity.user.entities.user import User
from domain.identity.user.events.user_events import (
    DomainEvent,
    UserCreated,
)
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from domain.identity.user.value_objects.user_state import UserState


class HasAggregateId(Protocol):
    id: str


def make_user(*, state: UserState) -> User:
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

class InMemoryUserRepository:

    def __init__(self) -> None:
        self.items: dict[str, HasAggregateId] = {}
        self.save_calls: int = 0

    def get_by_id(self, user_id: str) -> User:
        return cast(User, self.items.get(user_id))
    
    def save(self, user: User) -> int:
        self.items[user.id] = user
        self.save_calls += 1
        return user.version

    def create(self, user: User) -> int:
        if user.id in self.items:
            raise UserDuplicationError(
                code=ErrorCodes.DUPLICATE_USER,
                message=f"User with ID {user.id} already exists."
            )
        
        for item in self.items.values():
            is_same_business_key = (
                item.legal_identity.identity_type == user.legal_identity.identity_type and
                item.legal_identity.identity_number == user.legal_identity.identity_number and
                item.legal_identity.identity_issuer == user.legal_identity.identity_issuer
            )
            if is_same_business_key:
                raise UserDuplicationError(
                    code=ErrorCodes.DUPLICATE_USER,
                    message="An user with the same business key already exists."
                )
        
        self.items[user.id] = user
        return user.version
    

class FailingUserRepository(InMemoryUserRepository):
    def __init__(self, message: str = "database unavailable"):
        super().__init__()
        self.message = message

    def save(self, user: User) -> int:
        self.save_calls += 1
        raise UserTechnicalPersistenceError(
            code=ErrorCodes.DATABASE_ERROR,
            message="Failed to persist user due to a database error.",
            details={"error": self.message},
        )
    
    def create(self, user: User) -> int:
        self.save_calls += 1
        raise UserTechnicalPersistenceError(
            code=ErrorCodes.USER_CREATION_FAILED,
            message="Failed to create user due to a database error.",
            details={"error": self.message},   
        )
