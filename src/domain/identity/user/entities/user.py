from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Protocol
from uuid import uuid4

from domain.identity.user.errors.user_errors import (
    InvalidStateTransitionError,
    JustificationRequiredError,
    UserRequiredGuardianIDError,
)
from domain.identity.user.events.user_events import (
    UserActivated,
    UserCreated,
    UserInactivated,
    UserSuspended,
    UserUnlocked,
)
from domain.identity.user.value_objects.legal_identity import LegalIdentity
from domain.identity.user.value_objects.user_state import UserState
from domain.identity.user.value_objects.user_transition import UserTransition
from domain.shared.domain_error import DomainError
from domain.shared.domain_event import DomainEvent


class UserEventFactory(Protocol):
    def __call__(
            self,
            *,
            aggregate_id:str,
            actor_id: str,
            from_state:UserState,
            to_state: UserState,
            occurred_at: datetime,
            justification: str | None = None
    ) -> DomainEvent:
        ...


        
@dataclass
class User:
    """
        Aggregate Root: User
        - Rehydration-safe: validates invariants in __post_init__
        - State transitions are applied through command methods and recorded as:
        - StateTransition (VO)
        - DomainEvent (for integration after persistence)
        - Creation and updates are timestamped and attributed to an actor (created_by, created_at, etc.)

    """

    id: str
    legal_identity: LegalIdentity
    full_name: str
    birth_date: date
    created_by: str
    email: str | None = None
    guardian_id: str | None = None
    state: UserState = field(default=UserState.PENDING)

    created_at: datetime | None = None
    activated_at: datetime | None = None
    suspended_at: datetime | None = None
    inactivated_at: datetime | None = None
    unlocked_at: datetime | None = None

    transitions: list[UserTransition] = field(default_factory=list)
    _domain_events: list[DomainEvent] = field(default_factory=list)


# validation and invariants
    def __post_init__(self) -> None:
        self._normalize_datetimes()
        self._validate_fields()
        self._validate_state_integrity()


    def _validate_fields(self) -> None:
        string_fields = {
            "id": ("invalid_id", "id must have a valid ID format"),
            "full_name": ("invalid_full_name", "full_name is invalid"),
            "created_by": ("invalid_created_by", "created_by must have a valid ID format"),

        }
        for field_value, (code, message) in string_fields.items():
            value = getattr(self, field_value)
            if value is None or not value.strip():
                raise DomainError(code=code, message=message)
            
        if self.email is not None and not self.email.strip():
            raise DomainError(code="invalid_email", message="email cannot be empty if provided")
        
        if self.guardian_id is not None and not self.guardian_id.strip():
            raise DomainError(code="invalid_guardian_id", message="guardian_id cannot be empty if provided")
        
        if self.birth_date is None:
            raise DomainError(code="invalid_birth_date", message="birth_date is required")
        
        if self.birth_date > date.today():
            raise DomainError(code="invalid_birth_date", message="birth_date cannot be in the future")
        
        if self.legal_identity is None:
            raise DomainError(code="invalid_legal_identity", message="legal_identity is required")
        
        self._assert_guardian_required(self.guardian_id)
               
        
        
    def _normalize_datetimes(self) -> None:
        self.created_at = self._normalize_datetime_strict(self.created_at, field_name="created_at")

        if self.activated_at is not None:
            self.activated_at = self._normalize_datetime_strict(self.activated_at, field_name="activated_at")
        if self.suspended_at is not None:
            self.suspended_at = self._normalize_datetime_strict(self.suspended_at, field_name="suspended_at")
        if self.inactivated_at is not None:
            self.inactivated_at = self._normalize_datetime_strict(self.inactivated_at, field_name="inactivated_at")
        if self.unlocked_at is not None:
            self.unlocked_at = self._normalize_datetime_strict(self.unlocked_at, field_name="unlocked_at")
    
    
    # matrix de transições permitidas
    ALLOWED_TRANSITIONS = {
        UserState.PENDING:   {UserState.ACTIVE, UserState.INACTIVE},
        UserState.ACTIVE:    {UserState.SUSPENDED, UserState.INACTIVE},
        UserState.SUSPENDED: {UserState.INACTIVE, UserState.ACTIVE},
}

    def _assert_transition_allowed(self, to_state: UserState) -> None:
        allowed = self.ALLOWED_TRANSITIONS.get(self.state, set())

        if to_state not in allowed:
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message=f"Cannot transition from {self.state.value} to {to_state.value}.",
                details={
                    "from": self.state.value,
                    "to": to_state.value,
                    "allowed": [s.value for s in allowed],
                },
            )

    def _is_adult(self):
        today = date.today()
        age = today.year - self.birth_date.year

        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1

        return age >= 18
    
    def _assert_guardian_required(self, guardian_id: str | None) -> None:
        if not self._is_adult() and guardian_id is None:
            raise UserRequiredGuardianIDError(
                code="user_requires_guardian",
                message="User under 18 years old must have a guardian_id.",
                details={"birth_date": self.birth_date.isoformat()}
            )

    def _validate_state_integrity(self) -> None:
        # 4) State Consistency Matrix (Solution Implementation)
        # Def  : {State: (Required Fields, Forbidden Fields)}
        state_integrity_matrix = {
            UserState.ACTIVE: (
                ["created_at", "activated_at"],
            ),
            UserState.SUSPENDED: (
                ["suspended_at"],
            ),
            UserState.INACTIVE: (
                ["inactivated_at"]
            ),
            UserState.PENDING: (
                ["created_at"],              
            ),
        }
        state_integrity = state_integrity_matrix.get(self.state)
        if state_integrity is None:
            raise DomainError(
                code="invalid_state",
                message="User state is invalid",
                details={"state": str(self.state)},
            )
        required = state_integrity[0]

        # Validation A: Require mandatory fields for the current state.
        for field_name in required:
            if getattr(self, field_name) is None:
                raise DomainError(
                    code=f"missing_{field_name}",
                    message=f"User in state {self.state.value} requires field {field_name}.",
                    details={
                        "state": self.state.value,
                        "required_field": field_name,
                    }
                )


    @staticmethod
    def _normalize_datetime_strict(dt: datetime | None, *, field_name: str) -> datetime:
        """
        Normalize datetime to UTC-aware.
        Strict: does NOT accept None and does NOT silently 'invent' dates.
        """
        if dt is None:
            raise DomainError(
                code="invalid_datetime",
                message=f"{field_name} cannot be None",
                details={"field": field_name},
            )
        if not isinstance(dt, datetime):
            raise DomainError(
                code="invalid_datetime_type",
                message=f"{field_name} must be a datetime",
                details={"field": field_name, "type": type(dt).__name__},
            )
        if dt.tzinfo is None:
            return dt.replace(tzinfo=UTC)
        return dt.astimezone(UTC)

    
    @staticmethod
    def _occurred_at_or_now(occurred_at: datetime | None) -> datetime:
        """
        For commands only: if occurred_at is None, default to now (UTC).
        Otherwise, normalize strictly to UTC-aware.
        """
        if occurred_at is None:
            return datetime.now(UTC)
        return User._normalize_datetime_strict(occurred_at, field_name="occurred_at")

    # --- 
    def _apply_state_transition(
        self,
        *,
        to_state: UserState,
        actor_id: str,
        event_cls: UserEventFactory,
        occurred_at: datetime | None = None,
        justification: str | None = None,
    ) -> None:
        """
        Core logic for applying a state transition:
        1) Assert transition is allowed from current state to to_state.
        2) Validate justification if required for this transition.
        3) Create the Domain Event using event_cls (which should be specific to the transition
              e.g., UserActivated for ACTIVE, UserSuspended for SUSPENDED, etc.)
        4) Update User state and relevant timestamps.
        5) Record the UserTransition and DomainEvent for later persistence and integration.
        """
        
        utc_now = self._occurred_at_or_now(occurred_at)
        from_state = self.state

        new_transition=UserTransition(
            from_state=from_state,
            actor_id=actor_id,
            occurred_at=utc_now,
            to_state=to_state,
            justification=justification
        )

        # Instantiates the Domain Event (Event __post_init__ validations run here)
        new_event = event_cls(
            aggregate_id=self.id,
            actor_id=actor_id,
            from_state=from_state,
            to_state=to_state,
            occurred_at=utc_now,
            justification=justification,
        )            

        # Final Mutation (Happy Path: nothing here should throw exceptions)
        self.state = to_state
        if to_state == UserState.SUSPENDED:
            self.suspended_at = utc_now
        if to_state == UserState.INACTIVE:
            self.inactivated_at = utc_now
        if to_state == UserState.ACTIVE and from_state == UserState.SUSPENDED:
            self.unlocked_at = utc_now
        if to_state == UserState.ACTIVE and from_state == UserState.PENDING:
            if self.activated_at is None:
                self.activated_at = utc_now


        # Record in internal records
        self.transitions.append(new_transition)
        self._domain_events.append(new_event)

    def peek_domain_events(self) -> list[DomainEvent]:
        """
        Return pending domain events
        """
        return list(self._domain_events)


    def pull_domain_events(self) -> list[DomainEvent]:
        """
        Return and clear pending domain events recorded by this aggregate.
        This is a "pull" operation:
        - returns a snapshot of `_domain_events`;
        - clears the internal buffer (subsequent calls return an empty list).

        Intended to be called by the Application Layer once per use case.
        """

        domain_events = list(self._domain_events)
        self._domain_events.clear()
        return domain_events


    # --- Factory method for creation with event recording ---
    @classmethod
    def create(
            cls,
            *,
            legal_identity: LegalIdentity,
            full_name: str,
            birth_date: date,
            created_by: str,
            email: str | None = None,
            guardian_id: str | None = None,
            occurred_at: datetime | None = None
        ) -> User:

        created_at = cls._occurred_at_or_now(occurred_at)

        user = cls(
            id=str(uuid4()),
            legal_identity=legal_identity,
            full_name=full_name,
            birth_date=birth_date,
            created_by=created_by,
            email=email,
            guardian_id=guardian_id,
            created_at=created_at
        )

        create_event = UserCreated(
            aggregate_id=user.id,
            actor_id=user.created_by,
            occurred_at=created_at,
            legal_identity=user.legal_identity,
            full_name=user.full_name,
            email=user.email,
            birth_date=user.birth_date,
            guardian_id=user.guardian_id
        )

        user._domain_events.append(create_event)

        return user
    
    # ------------ Command methods for state transitions ------------
    def activate(
            self,
            *,
            actor_id: str,
            occurred_at: datetime | None = None,

    ) -> None:
    
        self._assert_transition_allowed(UserState.ACTIVE)
        self._apply_state_transition(
            to_state=UserState.ACTIVE,
            actor_id=actor_id,
            event_cls=UserActivated,  # This should be a specific event for activation, e.g., UserActivated   
            occurred_at=occurred_at,
        )
        
    def suspend(
            self,
            *,
            actor_id: str,
            occurred_at: datetime | None = None,
            justification: str
    ) -> None:
        self._assert_transition_allowed(UserState.SUSPENDED)
        if not justification.strip():
            raise JustificationRequiredError(
                code="justification_required",
                message="Justification is required to suspend a user.",
                details={"transition": f"{self.state.value} -> {UserState.SUSPENDED.value}"}
            )
        self._apply_state_transition(
            to_state=UserState.SUSPENDED,
            actor_id=actor_id,
            event_cls=UserSuspended,  # This should be a specific event for suspension, e.g., UserSuspended
            occurred_at=occurred_at,
            justification=justification
        )


    def inactivate(
            self,
            *,
            actor_id: str,
            occurred_at: datetime | None = None,
            justification: str
    ) -> None:
        self._assert_transition_allowed(UserState.INACTIVE)
        if not justification.strip():
            raise JustificationRequiredError(
                code="justification_required",
                message="Justification is required to inactivate a user.",
                details={"transition": f"{self.state.value} -> {UserState.INACTIVE.value}"}
            )
        self._apply_state_transition(
            to_state=UserState.INACTIVE,
            actor_id=actor_id,
            event_cls=UserInactivated,
            occurred_at=occurred_at,
            justification=justification
        )

    def unlock(
            self,
            *,
            actor_id: str,
            occurred_at: datetime | None = None,
            justification: str
    ) -> None:
        self._assert_transition_allowed(UserState.ACTIVE)
        if self.state != UserState.SUSPENDED:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="User can only be unlocked from SUSPENDED state",
                details={
                    'event': "UserUnlocked",
                    'actual_state': self.state.value,
                    'expected_state': UserState.SUSPENDED.value
                }  
            )

        if not justification.strip():
            raise JustificationRequiredError(
                code="justification_required",
                message="Justification is required to unlock a user.",
                details={"transition": f"{self.state.value} -> {UserState.ACTIVE.value}"}
            )
        
        self._apply_state_transition(
            to_state=UserState.ACTIVE,
            actor_id=actor_id,
            event_cls=UserUnlocked,
            occurred_at=occurred_at,
            justification=justification
        )
