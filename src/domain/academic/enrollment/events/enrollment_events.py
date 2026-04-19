from dataclasses import dataclass

from domain.shared.domain_error import DomainError
from domain.shared.domain_event import DomainEvent

from ..errors.enrollment_errors import InvalidStateTransitionError
from ..value_objects.enrollment_status import EnrollmentState


@dataclass(frozen=True, kw_only=True)
class EnrollmentConcluded(DomainEvent):
    """
        Domain event: Enrollment has been successfully concluded.

        Emitted when an enrollment transitions to the CONCLUDED state after
        validating business rules (attendance, grades, period closure, etc.).
        "Rule 4.2
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
                message="Rule 4.2: Reactivation is only allowed from the SUSPENDED state."
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
        for field_name, (code, message) in id_fields.items():
            value = getattr(self, field_name)
            if value is None or not value.strip():
                raise DomainError(code=code, message=message)
