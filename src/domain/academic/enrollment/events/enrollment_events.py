from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from ..errors.enrollment_errors import DomainError, InvalidStateTransitionError
from ..value_objects.enrollment_status import EnrollmentState


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
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
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


@dataclass(frozen=True, kw_only=True)
class EnrollmentReactivated(DomainEvent):
    """
    Domain event: Enrollment has been reactivated.
    Emitted when a SUSPENDED enrollment returns to the ACTIVE state.
    """
    actor_id: str
    from_state: EnrollmentState
    to_state: EnrollmentState
    justification: str | None = None

    def __post_init__(self):
        if self.to_state != EnrollmentState.ACTIVE:
            raise InvalidStateTransitionError(
                code="invalid_event_state",
                message="EnrollmentReactivated event must have to_state=ACTIVE",
                details={
                    'event': "EnrollmentReactivated",
                    'actual_state': self.to_state.value,
                    'expected_state': EnrollmentState.ACTIVE.value
                }
            )
        if self.from_state != EnrollmentState.SUSPENDED:
            raise InvalidStateTransitionError(
                code="invalid_origin_state",
                message="Rule 4.2: Reactivation is only allowed from the LOCKED state."
            )
        
@dataclass(frozen=True, kw_only=True)
class EnrollmentCreated(DomainEvent):
    """
    Domain event: Enrollment has been created.
    Emitted when a new enrollment is successfully created in the system.
    """

    actor_id: str
    institution_id: str
    student_id: str
    class_group_id: str
    academic_period_id: str


    def __post_init__(self):
        id_fields = {
            "actor_id": ("invalid_actor_id", "Enrollment must have a valid actor ID"),
            "institution_id": ("invalid_institution_id", "Enrollment must have a valid institution ID"),
            "student_id": ("invalid_student_id", "Enrollment must have a student ID"),
            "class_group_id": ("invalid_class_group_id", "Enrollment must have a valid class group ID"),
            "academic_period_id": ("invalid_academic_period_id", "Enrollment must have a valid academic period ID"),
        }
        for field_value, (code, message) in id_fields.items():
            value = getattr(self, field_value)
            if value is None or not value.strip():
                raise DomainError(code=code, message=message)
