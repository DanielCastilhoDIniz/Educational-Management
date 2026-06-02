from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import ClassVar, Protocol
from uuid import uuid4

from domain.identity.role.errors.role_errors import (
    InvalidStateTransitionError,
)
from domain.identity.role.events.role_events import RoleCreated, RoleDeactivated, RoleReactivated
from domain.identity.role.value_objects.capability import Capability
from domain.identity.role.value_objects.role_status import RoleStatus
from domain.shared.domain_error import DomainError
from domain.shared.domain_event import DomainEvent


class RoleEventFactory(Protocol):
    def __call__(
            self,
            *,
            aggregate_id:str,
            actor_id: str,
            from_status:RoleStatus,
            to_status: RoleStatus,
            occurred_at: datetime
    ) -> DomainEvent:
        ...

@dataclass
class Role:
    """
        Aggregate Root: Role
        Role is a system concept—independent of any user or institution. 
        The link between a User, a Role, and an Institution is 
        the responsibility of the Membership aggregate.

        RoleStatus (VO)
        Capability (VO)
    """

    id: str
    name: str
    code: str
    level: int
    created_by: str
    created_at: datetime | None = None
    reactivated_at: datetime | None = None
    deactivated_at: datetime | None = None
    status: RoleStatus = field(default=RoleStatus.ACTIVE)


    _domain_events: list[DomainEvent] = field(default_factory=list)


    # validation and invariants
    def __post_init__(self) -> None:
        self._normalize_datetimes()
        self._validate_fields()
        self._validate_status_integrity()

    def _validate_fields(self) -> None:
        string_fields = {
            "id": ("invalid_id", "id must have a valid ID format"),
            "name": ("invalid_name", "name is invalid"),
            "code": ("invalid_code", "code is invalid"),
            "created_by": ("invalid_created_by", "created_by must have a valid ID format"),
        }

        for field_value, (code, message) in string_fields.items():
            value = getattr(self, field_value)
            if value is None or not value.strip():
                raise DomainError(code=code, message=message)
        
        if not isinstance(self.level, int):
            raise DomainError(code="invalid_level", message="level is invalid")
         
        if not (0 <= self.level <= 4):
            raise DomainError(
                code="invalid_level",
                message="level must be a value between 0 and 4",
                details={
                    "level": self.level
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


    def _normalize_datetimes(self) -> None:
        self.created_at = self._normalize_datetime_strict(self.created_at, field_name="created_at")
        if self.reactivated_at is not None:
            self.reactivated_at = self._normalize_datetime_strict(self.reactivated_at, field_name="reactivated_at")
        if self.deactivated_at is not None:
            self.deactivated_at = self._normalize_datetime_strict(self.deactivated_at, field_name="deactivated_at")

    # matrix allowed transitions
    ALLOWED_TRANSITIONS = {
        RoleStatus.ACTIVE:   {RoleStatus.INACTIVE},
        RoleStatus.INACTIVE: {RoleStatus.ACTIVE},
    }   
    
    def _assert_transition_allowed(self, to_status: RoleStatus) -> None:
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, set())

        if to_status not in allowed:
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message=f"Cannot transition from {self.status.value} to {to_status.value}.",
                details={
                    "from": self.status.value,
                    "to": to_status.value,
                    "allowed": [s.value for s in allowed],
                },
            )
    
    def _validate_status_integrity(self) -> None:

        # Status Consistency Matrix (Solution Implementation)
        # Def  : {State: (Required Fields, Forbidden Fields)}

        status_integrity_matrix = {
            RoleStatus.ACTIVE: (
                ["created_at"],
            ),
            RoleStatus.INACTIVE: (
                ["deactivated_at"],
            ),    
        }

        status_integrity = status_integrity_matrix.get(self.status)
        if status_integrity is None:
            raise DomainError(
                code="invalid_status",
                message="Role status is invalid",
                details={"state": str(self.status)},
            )
        required = status_integrity[0]

        for field_name in required:
            if getattr(self, field_name) is None:
                raise DomainError(
                    code=f"missing_{field_name}",
                    message=f"Role in status {self.status.value} requires field {field_name}.",
                    details={
                        "status": self.status.value,
                        "required_field": field_name,
                    }
                )
           
    @staticmethod
    def _occurred_at_or_now(occurred_at: datetime | None) -> datetime:
        """
        For commands only: if occurred_at is None, default to now (UTC).
        Otherwise, normalize strictly to UTC-aware.
        """
        if occurred_at is None:
            return datetime.now(UTC)
        return Role._normalize_datetime_strict(occurred_at, field_name="occurred_at")

    def _apply_status_transition(
            self,
            *,
            to_status: RoleStatus,
            actor_id: str,
            event_cls: RoleEventFactory,
            occurred_at: datetime | None = None,    
    ) -> None:
        """
        Core logic for applying a status transition:
        1) Assert transition is allowed from current status to to_status.
        2) Create the Domain Event using event_cls (which should be specific to the transition
              e.g., RoleActivated for ACTIVE, RoleSuspended for SUSPENDED, etc.)
        3) Update Role status and relevant timestamps.
        4) Record the RoleTransition and DomainEvent for later persistence and integration.
        """
        
        self._assert_transition_allowed(to_status)

        utc_now = self._occurred_at_or_now(occurred_at)
        from_status = self.status

        new_event = event_cls(
            aggregate_id=self.id,
            actor_id=actor_id,
            from_status=from_status,
            to_status=to_status,
            occurred_at=utc_now
        )

        self.status = to_status
        if to_status == RoleStatus.ACTIVE:
            self.reactivated_at = utc_now
        if to_status == RoleStatus.INACTIVE:
            self.deactivated_at = utc_now

        
        self._domain_events.append(new_event)

    
    def peek_domain_events(self) -> list[DomainEvent]:

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
    

    _CAPABILITY_MAP: ClassVar[dict[str, frozenset[Capability]]] = {

        "direcao_estrategica": frozenset({
            Capability.USER_CREATE,
            Capability.USER_ACTIVATE,
            Capability.USER_UNLOCK,
            Capability.MEMBERSHIP_CREATE,
            Capability.MEMBERSHIP_ACTIVATE,
            Capability.MEMBERSHIP_CLOSE,
            Capability.MEMBERSHIP_SUSPEND,
            Capability.INSTITUTION_CONFIGURE,
            Capability.STUDENT_CREATE,
            Capability.CLASS_GROUP_CREATE,
            Capability.GUARDIAN_CREATE,
            Capability.TEACHER_CREATE,
            Capability.TEACHER_ASSIGN,
            Capability.PERIOD_CLOSE,
            Capability.SCHOOL_YEAR_CREATE,
        }),

        "gestao_financeira": frozenset({
            Capability.MEMBERSHIP_ACTIVATE,
            Capability.MEMBERSHIP_SUSPEND,
        }),      

        "secretaria": frozenset({
            Capability.USER_CREATE,
            Capability.INSTITUTION_CONFIGURE, 
            Capability.ENROLLMENT_CREATE,
            Capability.ENROLLMENT_READ,
            Capability.ENROLLMENT_CANCEL,
            Capability.ENROLLMENT_REACTIVATE,
            Capability.ENROLLMENT_SUSPEND,
            Capability.ENROLLMENT_HISTORY_READ,
            Capability.STUDENT_CREATE,
            Capability.SCHOOL_YEAR_CREATE,
            Capability.CLASS_GROUP_CREATE,
            Capability.GUARDIAN_CREATE,
            Capability.TEACHER_CREATE,
            Capability.TEACHER_ASSIGN,
            Capability.MEMBERSHIP_CREATE,
            Capability.REPORT_OFFICIAL_ISSUE,
            Capability.REPORT_READ,
            Capability.REPORT_EXPORT,
            Capability.GRADEBOOK_STUDENT_READ,       
        }),

        "coordenacao": frozenset({
            Capability.ENROLLMENT_READ,
            Capability.ENROLLMENT_HISTORY_READ,
            Capability.GRADEBOOK_STUDENT_READ,
            Capability.TEACHER_ASSIGN,
            Capability.GRADE_RECORD,
            Capability.ATTENDANCE_RECORD,
            Capability.LESSON_RECORD,
            Capability.REPORT_READ,
            Capability.REPORT_EXPORT,
            Capability.REPORT_OFFICIAL_ISSUE,
            Capability.PERIOD_CLOSE
        }),

        "suporte_adm":frozenset({
            Capability.USER_UNLOCK,
            Capability.INSTITUTION_CONFIGURE,
            Capability.ENROLLMENT_READ,
            Capability.ENROLLMENT_HISTORY_READ,
            Capability.ENROLLMENT_CANCEL,
        }),

        "professor": frozenset({
            Capability.ATTENDANCE_RECORD,
            Capability.GRADE_RECORD,
            Capability.LESSON_RECORD,
            Capability.REPORT_EXPORT,
            Capability.REPORT_READ,
        }),

        "estudante": frozenset({
            Capability.GRADEBOOK_STUDENT_READ,
            Capability.DASHBOARD_STUDENT_READ
        }),

        "responsavel": frozenset({
            Capability.GRADEBOOK_STUDENT_READ,
            Capability.DASHBOARD_STUDENT_READ
        })
    }
    
    @property
    def capabilities(self) -> frozenset[Capability]:
        return self._CAPABILITY_MAP.get(self.code, frozenset())
    
    def has_capability(self, capability: Capability) -> bool:
        return capability in self.capabilities
    
    # --- Factory method for creation with event recording ---
    @classmethod
    def create(
            cls,
            *,
            name: str,
            code: str,
            level: int,
            created_by: str,
            occurred_at: datetime | None = None     
    ) -> Role:

        created_at = cls._occurred_at_or_now(occurred_at)

        role = cls(
            id=str(uuid4()),
            name=name,
            code=code,
            level=level,
            status=RoleStatus.ACTIVE,
            created_by=created_by,
            created_at=created_at,
        )

        create_event = RoleCreated(
            aggregate_id=role.id,
            actor_id=role.created_by,
            occurred_at=created_at,
            name=role.name,
            level=role.level,
            code=role.code
        )

        role._domain_events.append(create_event)

        return role

    def reactivate(
            self,
            *,
            actor_id: str,
            occurred_at: datetime | None = None,
    ) -> None:
        
        self._apply_status_transition(
            to_status=RoleStatus.ACTIVE,
            actor_id=actor_id,
            event_cls=RoleReactivated,
            occurred_at=occurred_at,
        ) 
    
    def deactivate(
            self,
            *,
            actor_id: str,
            occurred_at: datetime | None = None,
    ) -> None:
  
        self._apply_status_transition(
            to_status=RoleStatus.INACTIVE,
            actor_id=actor_id,
            event_cls=RoleDeactivated,
            occurred_at=occurred_at,
        ) 

      