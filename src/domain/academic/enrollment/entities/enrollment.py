from datetime import datetime, timezone

from dataclasses import dataclass, field
from typing import cast

from ..value_objects.enrollment_status import EnrollmentState
from ..value_objects.state_transition import StateTransition
from ..value_objects.conclusion_verdict import ConclusionVerdict

from ..events.enrollment_events import (
    DomainEvent,
    EnrollmentConcluded,
    EnrollmentCancelled,
    EnrollmentSuspended
)
from ..errors.enrollment_errors import (
    ConclusionNotAllowedError,
    JustificationRequiredError,
    EnrollmentNotActiveError,
    DomainError,
    InvalidStateTransitionError
)


@dataclass
class Enrollment:
    """
        Represents an Enrollment aggregate root in the educational domain.
        Handles the state management, transitions,
        and domain events for a student's enrollment.
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

    # Internal state history to track all lifecycle changes
    transitions: list[StateTransition] = field(
        default_factory=lambda: cast(list[StateTransition], []))

    # Stores events to be dispatched after successful database persistence
    _domain_events: list[DomainEvent] = field(
        default_factory=lambda: cast(list[DomainEvent], []))

    def __post_init__(self):
        """
        Validates the entity's integrity after initialization.
        Ensures the enrollment is in a consistent state.
        """
        if not self.id:
            raise DomainError(code="invalid_id",
                              message="Enrollment must have a valid ID",
                              details={"reasons": self.id})

        # Integrity rule: Concluded state requires a timestamp
        if self.state == EnrollmentState.CONCLUDED and not self.concluded_at:
            raise DomainError(
                code="missing_concluded_at",
                message="Concluded enrollment must have a conclusion date")

        if self.state == EnrollmentState.CANCELLED and not self.cancelled_at:
            raise DomainError(
                code="missing_cancelled_at",
                message="Cancelled enrollment must have a cancellation date")

        if self.state == EnrollmentState.SUSPENDED and not self.suspended_at:
            raise DomainError(
                code="missing_suspended_at",
                message="Suspended enrollment must have a suspension date")

    def conclude(self, *, actor_id: str,
                 verdict: ConclusionVerdict,
                 occurred_at: datetime | None = None,
                 justification: str | None = None) -> None:

        """
        Transitions the enrollment state to CONCLUDED.
        Validates business policies through a
        verdict and records the transition.
        """

        if occurred_at is None:
            occurred_at = datetime.now(timezone.utc)

        if self.state == EnrollmentState.CONCLUDED:
            return

        if self.state != EnrollmentState.ACTIVE:
            raise EnrollmentNotActiveError(
                code="enrollment_not_active",
                message="Enrollment must be ACTIVE to be concluded.",
                details={"current_state": self.state.value,
                         "required_state": EnrollmentState.ACTIVE.value,
                         "attempted_action": "conclude"}
                )

        if verdict.is_allowed is False:
            raise ConclusionNotAllowedError(
                code="enrollment_conclusion_not_allowed",
                message="Conclusion is not allowed by policy",
                details={"reasons": verdict.reasons,
                         "attempted_action": "conclude"}
            )

        if verdict.requires_justification:
            if not justification or not justification.strip():
                raise JustificationRequiredError(
                    code="justification_required",
                    message="Justification is required to conclude enrollment",
                    details={"policy": "requires_justification"}
                )

        from_state = self.state
        # Persist the transition in history for audit purposes
        self.transitions.append(
            StateTransition(
                from_state=from_state,
                actor_id=actor_id,
                to_state=EnrollmentState.CONCLUDED,
                occurred_at=occurred_at,
                justification=justification
            )
        )
        self.state = EnrollmentState.CONCLUDED
        self.concluded_at = occurred_at

        # Record the Domain Event to notify other
        # subdomains (Certificates, Billing)
        self._domain_events.append(
            EnrollmentConcluded(
                aggregate_id=self.id,
                occurred_at=occurred_at,
                actor_id=actor_id,
                from_state=from_state,
                to_state=EnrollmentState.CONCLUDED,
                justification=justification,

            )
        )

    def pull_domain_events(self) -> list[DomainEvent]:
        """
        Extracts and clears all accumulated domain events.
        Useful for dispatching events after a successful transaction.
        """
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def is_final(self) -> bool:

        """
        Checks if the enrollment has reached a
        terminal state where no further actions are allowed.
        """
        return self.state in {
            EnrollmentState.CONCLUDED,
            EnrollmentState.CANCELLED
        }

    def cancel(
            self, *,
            actor_id: str,
            occurred_at: datetime | None = None,
            justification: str,
    ):
        """
        Transitions the enrollment state to CANCELLED.
        """

        if self.state == EnrollmentState.CANCELLED:
            return

        if self.state == EnrollmentState.CONCLUDED:
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message="state transition not allowed",
                details={
                    'current_state': self.state.value,
                    'attempted_action': 'cancel',
                    'allowed_from_states': ['active', 'suspended'],
                    'forbidden_reason': self.state.value}
            )

        if not justification or not justification.strip():
            raise JustificationRequiredError(
                code="required_justification",
                message="justification is required to cancel enrollment",
                details={'policy': 'justification_required'}
            )

        from_state = self.state
        occurred_at = occurred_at or datetime.now(timezone.utc)

        self.transitions.append(
            StateTransition(
                actor_id=actor_id,
                from_state=from_state,
                occurred_at=occurred_at,
                to_state=EnrollmentState.CANCELLED,
                justification=justification
            )
        )
        self.state = EnrollmentState.CANCELLED
        self.cancelled_at = occurred_at

        self._domain_events.append(
            EnrollmentCancelled(
                aggregate_id=self.id,
                actor_id=actor_id,
                from_state=from_state,
                occurred_at=occurred_at,
                to_state=EnrollmentState.CANCELLED,
                justification=justification
            )
        )

    def suspend(self,
                *,
                actor_id: str,
                occurred_at: datetime | None = None,
                justification: str,
                ):

        """
        Transitions the enrollment state to SUSPENDED.
        """
        if self.state == EnrollmentState.SUSPENDED:
            return

        if self.state == EnrollmentState.CONCLUDED:
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message="state transition not allowed",
                details={
                    'current_state': self.state.value,
                    'attempted_action': 'suspend',
                    'allowed_from_states': ['active'],
                    'forbidden_reason': self.state.value}
            )

        if self.state == EnrollmentState.CANCELLED:
            raise InvalidStateTransitionError(
                code="invalid_state_transition",
                message="state transition not allowed",
                details={
                    'current_state': self.state.value,
                    'attempted_action': 'suspend',
                    'allowed_from_states': ['active'],
                    'forbidden_reason': self.state.value}
            )
        if not justification or not justification.strip():
            raise JustificationRequiredError(
                code="required_justification",
                message="justification is required to suspend enrollment",
                details={'policy': 'justification_required'}
            )

        from_state = self.state
        occurred_at = occurred_at or datetime.now(timezone.utc)

        self.transitions.append(
            StateTransition(
                actor_id=actor_id,
                from_state=from_state,
                occurred_at=occurred_at,
                to_state=EnrollmentState.SUSPENDED,
                justification=justification
            )
        )
        self.state = EnrollmentState.SUSPENDED
        self.suspended_at = occurred_at

        self._domain_events.append(
            EnrollmentSuspended(
                aggregate_id=self.id,
                actor_id=actor_id,
                from_state=from_state,
                occurred_at=occurred_at,
                to_state=EnrollmentState.SUSPENDED,
                justification=justification
            )
        )
