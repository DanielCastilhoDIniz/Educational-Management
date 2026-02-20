from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Type

from ..value_objects.enrollment_status import EnrollmentState
from ..value_objects.state_transition import StateTransition
from ..value_objects.conclusion_verdict import ConclusionVerdict

from ..events.enrollment_events import (
    DomainEvent,
    EnrollmentConcluded,
    EnrollmentCancelled,
    EnrollmentSuspended,
    EnrollmentReactivated,
)
from ..errors.enrollment_errors import (
    ConclusionNotAllowedError,
    JustificationRequiredError,
    EnrollmentNotActiveError,
    DomainError,
    InvalidStateTransitionError,
)


@dataclass
class Enrollment:
    """
    Aggregate Root: Enrollment

    - Rehydration-safe: validates invariants in __post_init__
    - State transitions are applied through command methods and recorded as:
      - StateTransition (VO)
      - DomainEvent (for integration after persistence)
    """
    id: str
    student_id: str
    class_group_id: str
    academic_period_id: str
    state: EnrollmentState
    created_at: datetime

    concluded_at: datetime | None = None
    cancelled_at: datetime | None = None
    suspended_at: datetime | None = None

    version: int = 1

    transitions: list[StateTransition] = field(default_factory=list)
    _domain_events: list[DomainEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_identity()
        self._normalize_and_validate_state()
        self._validate_version()
        self._normalize_datetimes()
        self._validate_state_integrity()

    def _validate_identity(self) -> None:
        if not self.id or not self.id.strip():
            raise DomainError(code="invalid_id", message="Enrollment must have a valid ID")

    def _normalize_and_validate_state(self) -> None:
        if isinstance(self.state, str):
            try:
                self.state = EnrollmentState(self.state)
            except ValueError as exc:
                raise DomainError(
                    code="invalid_state",
                    message="Enrollment state is invalid",
                    details={"state": self.state},
                ) from exc
        elif not isinstance(self.state, EnrollmentState):
            raise DomainError(
                code="invalid_state_type",
                message="Enrollment state must be EnrollmentState or valid state string",
                details={"type": type(self.state).__name__},
            )

    def _validate_version(self) -> None:
        if not isinstance(self.version, int) or self.version < 1:
            raise DomainError(
                code="invalid_version",
                message="Enrollment version must be an integer >= 1",
                details={"version": self.version},
            )

    def _normalize_datetimes(self) -> None:
        self.created_at = self._normalize_datetime_strict(self.created_at, field_name="created_at")

        if self.concluded_at is not None:
            self.concluded_at = self._normalize_datetime_strict(self.concluded_at, field_name="concluded_at")
        if self.cancelled_at is not None:
            self.cancelled_at = self._normalize_datetime_strict(self.cancelled_at, field_name="cancelled_at")
        if self.suspended_at is not None:
            self.suspended_at = self._normalize_datetime_strict(self.suspended_at, field_name="suspended_at")

    def _validate_state_integrity(self) -> None:
        # 4) State Consistency Matrix (Solution Implementation)
        # Define: {State: (Required Fields, Forbidden Fields)}
        state_integrity_matrix = {
            EnrollmentState.ACTIVE: (
                [],
                ["concluded_at", "cancelled_at", "suspended_at"]
            ),
            EnrollmentState.SUSPENDED: (
                ["suspended_at"],
                ["concluded_at", "cancelled_at"]
            ),
            EnrollmentState.CONCLUDED: (
                ["concluded_at"],
                ["cancelled_at", "suspended_at"]
            ),
            EnrollmentState.CANCELLED: (
                ["cancelled_at"],
                ["concluded_at", "suspended_at"]
            ),
        }

        state_integrity = state_integrity_matrix.get(self.state)
        if state_integrity is None:
            raise DomainError(
                code="invalid_state",
                message="Enrollment state is invalid",
                details={"state": str(self.state)},
            )
        required, forbidden = state_integrity

        # Validation A: Require mandatory fields for the current state.
        for field_name in required:
            if getattr(self, field_name) is None:
                raise DomainError(
                    code=f"missing_{field_name}",
                    message=f"Enrollment {self.state.value} requires filling out {field_name}."
                )

        # Validation B: Prohibit fields from other states (Total Uniqueness)
        for field_name in forbidden:
            if getattr(self, field_name) is not None:
                raise DomainError(
                    code="inconsistent_timestamps",
                    message=f"Registration number {self.state.value} cannot have {field_name} field in.",
                    details={"state": self.state.value, "forbidden_field": field_name}
                )

    @staticmethod
    def _normalize_datetime_strict(dt: datetime, *, field_name: str) -> datetime:
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
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def _occurred_at_or_now(occurred_at: Optional[datetime]) -> datetime:
        """
        For commands only: if occurred_at is None, default to now (UTC).
        Otherwise, normalize strictly to UTC-aware.
        """
        if occurred_at is None:
            return datetime.now(timezone.utc)
        return Enrollment._normalize_datetime_strict(occurred_at, field_name="occurred_at")

    def _apply_state_transition(
        self,
        *,
        to_state: EnrollmentState,
        actor_id: str,
        event_cls: Type[DomainEvent],
        occurred_at: Optional[datetime] = None,
        justification: Optional[str] = None,
    ) -> None:
        """
        Atomic transition: logic first, mutation last.
        Ensures the aggregate never reaches an inconsistent state if an
        exception occurs during object instantiation.
        """
        # 1. Preparation and Validation (It can fail here without corrupting the state)
        utc_now = self._occurred_at_or_now(occurred_at)
        from_state = self.state

        # Instancia o VO de Transição
        new_transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            actor_id=actor_id,
            occurred_at=utc_now,
            justification=justification,
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

        # 2. Final Mutation (Happy Path: nothing here should throw exceptions)
        # Total reset to satisfy the Consistency Matrix
        self.concluded_at = None
        self.cancelled_at = None
        self.suspended_at = None

        self.state = to_state
        if to_state == EnrollmentState.CONCLUDED:
            self.concluded_at = utc_now
        elif to_state == EnrollmentState.CANCELLED:
            self.cancelled_at = utc_now
        elif to_state == EnrollmentState.SUSPENDED:
            self.suspended_at = utc_now

        # Record in internal records
        self.transitions.append(new_transition)
        self._domain_events.append(new_event)

    def pull_domain_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def is_final(self) -> bool:
        return self.state in {EnrollmentState.CONCLUDED, EnrollmentState.CANCELLED}

    def conclude(
        self,
        *,
        actor_id: str,
        verdict: ConclusionVerdict,
        occurred_at: Optional[datetime] = None,
        justification: Optional[str] = None,
    ) -> None:
        if self.state == EnrollmentState.CONCLUDED:
            return

        if self.state != EnrollmentState.ACTIVE:
            raise EnrollmentNotActiveError(
                code="enrollment_not_active",
                message=f"Cannot conclude enrollment in state {self.state.value}",
                details={"current_state": self.state.value},
            )

        if not verdict.is_allowed:
            raise ConclusionNotAllowedError(
                code="conclusion_not_allowed",
                message="Conclusion blocked by policy",
                details={"reasons": verdict.reasons},
            )

        if verdict.requires_justification and not (justification and justification.strip()):
            raise JustificationRequiredError(
                code="justification_required",
                message="Justification required by verdict",
            )

        self._apply_state_transition(
            to_state=EnrollmentState.CONCLUDED,
            actor_id=actor_id,
            event_cls=EnrollmentConcluded,
            occurred_at=occurred_at,
            justification=justification,
        )

    def cancel(
        self,
        *,
        actor_id: str,
        justification: str,
        occurred_at: Optional[datetime] = None,
    ) -> None:
        if self.state == EnrollmentState.CANCELLED:
            return

        if self.is_final():
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message=f"Cannot cancel from terminal state {self.state.value}",
                details={"current_state": self.state.value},
            )

        if not justification or not justification.strip():
            raise JustificationRequiredError(
                code="required_justification",
                message="Justification required for cancellation",
            )

        self._apply_state_transition(
            to_state=EnrollmentState.CANCELLED,
            actor_id=actor_id,
            event_cls=EnrollmentCancelled,
            occurred_at=occurred_at,
            justification=justification,
        )

    def suspend(
        self,
        *,
        actor_id: str,
        justification: str,
        occurred_at: Optional[datetime] = None,
    ) -> None:
        if self.state == EnrollmentState.SUSPENDED:
            return

        if self.state != EnrollmentState.ACTIVE:
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message=f"Only ACTIVE enrollments can be suspended. Current: {self.state.value}",
                details={"current_state": self.state.value},
            )

        if not justification or not justification.strip():
            raise JustificationRequiredError(
                code="required_justification",
                message="Justification required for suspension",
            )

        self._apply_state_transition(
            to_state=EnrollmentState.SUSPENDED,
            actor_id=actor_id,
            event_cls=EnrollmentSuspended,
            occurred_at=occurred_at,
            justification=justification,
        )

    def reactivate(
            self,
            *,
            actor_id: str,
            justification: str,
            occurred_at: Optional[datetime] = None
            ) -> None:
        """
            Transitions the enrollment back to ACTIVE state.
            Strict Rule: Only allowed from SUSPENDED state.
        """
        if self.state == EnrollmentState.ACTIVE:
            return

        if self.state != EnrollmentState.SUSPENDED:
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message=f"Reactivation is only allowed for SUSPENDED enrollments. Current state: {self.state.value}",
                details={
                    "current_state": self.state.value,
                    "required_state": EnrollmentState.SUSPENDED.value,
                    "attempted_action": "reactivate"
                }
            )

        if not justification or not justification.strip():
            raise JustificationRequiredError(
                code="required_justification",
                message="A justification is mandatory to reactivate an enrollment."
            )

        self._apply_state_transition(
            to_state=EnrollmentState.ACTIVE,
            actor_id=actor_id,
            event_cls=EnrollmentReactivated,
            occurred_at=occurred_at,
            justification=justification
        )
