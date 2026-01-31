from datetime import datetime
from ..value_objects.enrollment_status import EnrollmentState

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    aggregate_id: str
    occurred_at: datetime = field(default_factory=datetime.now)
    event_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True, kw_only=True)
class EnrollmentConcluded(DomainEvent):
    """
        Enrollment concluded event
    """
    actor_id: str
    from_state: EnrollmentState
    to_state: EnrollmentState
    justification: str | None = None

