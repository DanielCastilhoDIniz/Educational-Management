from .enrollment_status import EnrollmentState

from datetime import datetime, timezone

from ..errors.enrollment_errors import DomainError

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
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    justification: str | None = None

    def __post_init__(self):
        if self.occurred_at is None:
            raise DomainError(
                code="invalid_occurred_at",
                message="occurred_at cannot be None",
                details={"reasons": self.occurred_at}
            )
        if not self.actor_id or not self.actor_id.strip():
            raise DomainError(
                code="invalid_actor_id",
                message="actor_id cannot be empty",
                details={"reasons": self.actor_id}
            )

        if self.occurred_at.tzinfo is None:
            object.__setattr__(self, 'occurred_at', self.occurred_at.replace(tzinfo=timezone.utc))
        else:
            object.__setattr__(self, 'occurred_at', self.occurred_at.astimezone(timezone.utc))

        if self.from_state == self.to_state:
            raise DomainError(
                code="invalid_state_transition",
                message="from_state and to_state cannot be the same",
                details={"from_state": self.from_state.value, "to_state": self.to_state.value})
