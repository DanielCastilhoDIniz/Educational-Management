
from dataclasses import dataclass
from datetime import date

from domain.identity.user.errors.user_errors import (
    InvalidStateTransitionError,
    UserRequiredGuardianIDError,
)
from domain.identity.user.value_objects.legal_identity import LegalIdentity
from domain.identity.user.value_objects.user_state import UserState
from domain.shared.domain_error import DomainError
from domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class UserCreated(DomainEvent):

    actor_id:str
    legal_identity: LegalIdentity
    full_name: str
    email: str | None = None
    birth_date: date
    guardian_id: str | None = None

    def _is_adult(self):
        today = date.today()
        age = today.year - self.birth_date.year

        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1

        return age >= 18


    def __post_init__(self):
        required_fields_str = {
            "actor_id": ("invalid_actor_id", "User must have a valid actor ID"),
            "full_name": ("invalid_full_name", "User must have a valid full name"),      
        }
        for field_value, (code, message) in required_fields_str.items():
            value_str = getattr(self,field_value)
            if value_str is None or not value_str.strip():
                raise DomainError(code=code, message=message)
            
        required_fields = {
            "legal_identity": ("invalid_legal_identity", "User must have a valid legal identity"),
            "birth_date": ("invalid_birth_date", "User must have a valid birth date"),        
        }

        for field_value, (code, message) in required_fields.items():
            value = getattr(self,field_value)
            if value is None or not value:
                raise DomainError(code=code, message=message)
            
        if not self._is_adult() and self.guardian_id is None:
            raise UserRequiredGuardianIDError(
                code="user_requires_guardian",
                message="user under 18 years old must have a guardian_id",
                details={"birth_date": self.birth_date.isoformat()}
            )           
  

@dataclass(frozen=True, kw_only=True)
class UserActivated(DomainEvent):

    from_state: UserState
    actor_id:str
    to_state: UserState
    justification: str | None = None

    def __post_init__(self):
        if self.from_state !=  UserState.PENDING:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserActivated event must have from_state=PENDING",
                details={
                    'event': "UserActivated",
                    'actual_state': self.from_state.value,
                    'expected_state': UserState.PENDING.value
                }
            )
        if self.to_state !=  UserState.ACTIVE:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserActivated event must have to_state=ACTIVE",
                details={
                    'event': "UserActivated",
                    'actual_state': self.to_state.value,
                    'expected_state': UserState.ACTIVE.value
                }
            )

@dataclass(frozen=True, kw_only=True)
class UserSuspended(DomainEvent):

    from_state: UserState
    actor_id:str
    to_state: UserState
    justification: str | None = None

    def __post_init__(self):
        if self.from_state !=  UserState.ACTIVE:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserSuspended event must have from_state=ACTIVE",
                details={
                    'event': "UserSuspended",
                    'actual_state': self.from_state.value,
                    'expected_state': UserState.ACTIVE.value
                }
            )
        if self.to_state !=  UserState.SUSPENDED:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserSuspended event must have to_state=SUSPENDED",
                details={
                    'event': "UserSuspended",
                    'actual_state': self.to_state.value,
                    'expected_state': UserState.SUSPENDED.value
                }
            )


@dataclass(frozen=True, kw_only=True)
class UserInactivated(DomainEvent):

    from_state: UserState
    actor_id:str
    to_state: UserState
    justification: str | None = None

    def __post_init__(self):
        if self.from_state not in (UserState.ACTIVE, UserState.SUSPENDED):

            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserInactivated event must have from_state=ACTIVE or SUSPENDED",
                details={
                    'event': "UserInactivated",
                    'actual_state': self.from_state.value,
                    'expected_state':f"{UserState.ACTIVE.value} or {UserState.SUSPENDED.value}"
                }
            )
        if self.to_state !=  UserState.INACTIVE:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserInactivated event must have to_state=INACTIVE",
                details={
                    'event': "UserInactivated",
                    'actual_state': self.to_state.value,
                    'expected_state': UserState.INACTIVE.value,
                }
            )


@dataclass(frozen=True, kw_only=True)
class UserUnlocked(DomainEvent):

    from_state: UserState
    actor_id:str
    to_state: UserState
    justification: str | None = None

    def __post_init__(self):

        if self.from_state !=  UserState.SUSPENDED:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserUnlocked event must have from_state=SUSPENDED",
                details={
                    'event': "UserUnlocked",
                    'actual_state': self.from_state.value,
                    'expected_state': UserState.SUSPENDED.value
                }
            )
        if self.to_state !=  UserState.ACTIVE:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="UserUnlocked event must have to_state=ACTIVE",
                details={
                    'event': "UserUnlocked",
                    'actual_state': self.to_state.value,
                    'expected_state': UserState.ACTIVE.value
                }
            )

