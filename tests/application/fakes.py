from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol, cast

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.errors.persistence_errors import (
    EnrollmentCreationError,
    EnrollmentDuplicationError,
)
from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import (
    DomainEvent,
    EnrollmentCancelled,
    EnrollmentConcluded,
    EnrollmentReactivated,
    EnrollmentSuspended,
)
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


class HasAggregateId(Protocol):
    id: str


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    now = datetime.now(UTC)

    concluded_at = now if state == EnrollmentState.CONCLUDED else None
    suspended_at = now if state == EnrollmentState.SUSPENDED else None
    cancelled_at = now if state == EnrollmentState.CANCELLED else None
    reactivated_at = None

    return Enrollment(
        id="enr-1",
        institution_id="inst-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        concluded_at=concluded_at,
        suspended_at=suspended_at,
        cancelled_at=cancelled_at,
        reactivated_at=reactivated_at,

    )


class InMemoryEnrollmentRepository:
    def __init__(self) -> None:
        self.items: dict[str, HasAggregateId] = {}
        self.save_calls: int = 0

    def get_by_id(self, enrollment_id: str) -> Enrollment:
        return cast(Enrollment, self.items.get(enrollment_id))

    def save(self, enrollment: Enrollment) -> int:
        self.items[enrollment.id] = enrollment
        self.save_calls += 1
        return enrollment.version +1

    def seed(self, enrollment: HasAggregateId) -> None:
        self.items[enrollment.id] = enrollment

    def create(self, enrollment: Enrollment) -> int:
        self.items[enrollment.id] = enrollment
        return enrollment.version
    
    def exist_by_business_key(self, institution_id: str, student_id: str, class_group_id: str, academic_period_id: str) -> bool:
            for item in self.items.values():
                if not isinstance(item, Enrollment):
                    continue
                if (
                    item.institution_id == institution_id and
                    item.student_id == student_id and
                    item.class_group_id == class_group_id and
                    item.academic_period_id == academic_period_id
                ):
                    return True
            return False


class FailingEnrollmentRepository(InMemoryEnrollmentRepository):
    def __init__(self, message: str = "database unavailable"):
        super().__init__()
        self.message = message

    def save(self, enrollment: Enrollment) -> int:
        self.save_calls += 1
        raise RuntimeError(self.message)
    
    def create(self, enrollment: Enrollment) -> int:
        self.save_calls += 1
        raise EnrollmentCreationError(
            code=ErrorCodes.ENROLLMENT_CREATION_FAILED,
            message="Failed to create enrollment due to an infrastructure error."
        )

class FailingCreateInRepository(InMemoryEnrollmentRepository):
        
    def __init__(self, message: str = "enrollment create duplicity"):
        super().__init__()
        self.message = message

    def create(self, enrollment: Enrollment) -> int:
        self.save_calls += 1
        raise EnrollmentDuplicationError(
            code=ErrorCodes.DUPLICATE_ENROLLMENT,
            message="An enrollment with the same identifier already exists."
        )
    
class ScriptedEnrollment:
    def __init__(
            self,
            *,
            enrollment_id: str,
            state: EnrollmentState,
            next_state: EnrollmentState,
            command_events: list[DomainEvent],
    ) -> None:
        self.id = enrollment_id
        self.state = state
        self._next_state = next_state
        self._command_events = list(command_events)
        self._pending_events: list[DomainEvent] = []

    def cancel(self, **_: object) -> None:
        self._apply_script()

    def suspend(self, **_: object) -> None:
        self._apply_script()

    def conclude(self, **_: object) -> None:
        self._apply_script()
    
    def reactivate(self, **_: object) -> None:
        self._apply_script()
        
    def create(self, **_: object) -> None:
        self._apply_script()
        
    def peek_domain_events(self) -> list[DomainEvent]:
        return list(self._pending_events)

    def pull_domain_events(self) -> list[DomainEvent]:
        pending_events = list(self._pending_events)
        self._pending_events.clear()
        return pending_events

    def _apply_script(self) -> None:
        self.state = self._next_state
        self._pending_events = list(self._command_events)


def make_cancelled_event(
        *,
        aggregate_id: str = "enr-1",
        from_state: EnrollmentState = EnrollmentState.ACTIVE,
) -> EnrollmentCancelled:
    return EnrollmentCancelled(
        aggregate_id=aggregate_id,
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
        from_state=from_state,
        to_state=EnrollmentState.CANCELLED,
        justification="test",
    )


def make_suspended_event(
        *,
        aggregate_id: str = "enr-1",
        from_state: EnrollmentState = EnrollmentState.ACTIVE,
) -> EnrollmentSuspended:
    return EnrollmentSuspended(
        aggregate_id=aggregate_id,
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
        from_state=from_state,
        to_state=EnrollmentState.SUSPENDED,
        justification="test",
    )


def make_concluded_event(
        *,
        aggregate_id: str = "enr-1",
        from_state: EnrollmentState = EnrollmentState.ACTIVE,
) -> EnrollmentConcluded:
    return EnrollmentConcluded(
        aggregate_id=aggregate_id,
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
        from_state=from_state,
        to_state=EnrollmentState.CONCLUDED,
        justification="test",
    )

def make_reactivated_event(
        *,
        aggregate_id: str = "enr-1",
        from_state: EnrollmentState = EnrollmentState.SUSPENDED,
) -> EnrollmentReactivated:
    return EnrollmentReactivated(
        aggregate_id=aggregate_id,
        actor_id="user-1",
        justification="test",
        occurred_at=datetime.now(UTC),
        from_state=from_state,
        to_state=EnrollmentState.ACTIVE,
    )

