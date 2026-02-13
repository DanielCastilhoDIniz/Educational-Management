from datetime import datetime

from ..value_objects.enrollment_status import EnrollmentState

from ..errors.enrollment_errors import InvalidStateTransitionError

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """
        Base class for all domain events.

        Represents an immutable fact that occurred in the business domain.
        All events are frozen (immutable) and
        use keyword-only arguments for clarity.

    Attributes:
        aggregate_id: Unique identifier of the affected aggregate root.
        occurred_at: Date and time when the event actually occurred.
        event_id: Globally unique identifier of the event (UUID v4)
    """
    aggregate_id: str
    occurred_at: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True, kw_only=True)
class EnrollmentConcluded(DomainEvent):
    """
        Domain event: Enrollment has been successfully concluded.

        Emitted when an enrollment transitions to the CONCLUDED state after
        validating business rules (attendance, grades, period closure, etc.).
    """

    actor_id: str
    from_state: EnrollmentState
    to_state: EnrollmentState
    justification: str | None = None

    def __post_init__(self):
        if self.to_state != EnrollmentState.CONCLUDED:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="EnrollmentState event must have to_state=CONCLUDED",
                details={
                    'event': "EnrollmentConcluded",
                    'actual_state': self.to_state.value,
                    'expected_state': EnrollmentState.CONCLUDED.value,
                }
            )


@dataclass(frozen=True, kw_only=True)
class EnrollmentCancelled(DomainEvent):
    """
    Domain event: Enrollment has been cancelled.

    Emitted when an enrollment is cancelled due to administrative,
    pedagogical, or student/responsible request reasons.
    """
    actor_id: str
    from_state: EnrollmentState
    to_state: EnrollmentState
    justification: str | None = None

    def __post_init__(self):
        if self.to_state != EnrollmentState.CANCELLED:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="EnrollmentState event must have to_state=CANCELLED",
                details={
                    'event': "EnrollmentCancelled",
                    'actual_state': self.to_state.value,
                    'expected_state': EnrollmentState.CANCELLED.value
                }
            )


@dataclass(frozen=True, kw_only=True)
class EnrollmentSuspended(DomainEvent):
    """
        Domain event: Enrollment has been suspended.
        Represents a temporary suspension of an enrollment
        (e.g., due to non-payment,
        disciplinary process, legal request, etc.).
    """

    actor_id: str
    from_state: EnrollmentState
    to_state: EnrollmentState
    justification: str | None = None

    def __post_init__(self):
        if self.to_state != EnrollmentState.SUSPENDED:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="EnrollmentState event must have to_state=SUSPENDED",
                details={
                    'event': "EnrollmentSuspended",
                    'actual_state': self.to_state.value,
                    'expected_state': EnrollmentState.SUSPENDED.value
                }
            )
# verificar se aqui é o melhor local para reativação de matricula. <---------