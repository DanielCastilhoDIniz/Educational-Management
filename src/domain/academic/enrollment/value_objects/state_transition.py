from .enrollment_status import EnrollmentState
from datetime import datetime

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StateTransition:
    """
        Transition between enrollment states
        from_state -> to_state
        occurred_at date of transition
        justification: is optional
    """

    from_state: EnrollmentState
    actor_id: str
    to_state: EnrollmentState
    occurred_at: datetime = field(default_factory=datetime.now)
    justification: str | None = None
