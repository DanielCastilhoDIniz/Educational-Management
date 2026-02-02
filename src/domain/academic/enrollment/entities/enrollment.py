from datetime import datetime

from dataclasses import dataclass, field
from typing import cast

from ..value_objects.enrollment_status import EnrollmentState
from ..value_objects.state_transition import StateTransition
from ..value_objects.conclusion_verdict import ConclusionVerdict

from ..events.enrollment_events import (
    DomainEvent,
    EnrollmentConcluded
)
from ..errors.enrollment_errors import (
    ConclusionNotAllowedError,
    JustificationRequiredError,
    EnrollmentNotActiveError,

)


@dataclass
class Enrollment:
    """
        Enrollment entity

    """
    id: str
    student_id: str
    class_group_id: str
    academic_period_id: str
    state: EnrollmentState
    created_at: datetime
    concluded_at: datetime | None = None
    transitions: list[StateTransition] = field(
        default_factory=lambda: cast(list[StateTransition], []))
    _domain_events: list[DomainEvent] = field(
        default_factory=lambda: cast(list[DomainEvent], []))

    def conclude(self, *, actor_id: str,
                 verdict: ConclusionVerdict,
                 occurred_at: datetime | None = None,
                 justification: str | None = None) -> None:

        if occurred_at is None:
            occurred_at = datetime.now()

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

        self._domain_events.append(
            EnrollmentConcluded(
                aggregate_id=self.id,
                occurred_at=occurred_at,
                actor_id=actor_id,
                from_state=from_state,
                to_state=EnrollmentState.CONCLUDED,
                justification=justification
            )
        )

    def pull_domain_events(self) -> list[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events

    def is_final(self) -> bool:
        return self.state in {
            EnrollmentState.CONCLUDED,
            EnrollmentState.CANCELLED
        }







