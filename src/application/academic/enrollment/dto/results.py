from __future__ import annotations
from dataclasses import dataclass

from domain.academic.enrollment.events.enrollment_events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ApplicationResult:
    """
    Base class for application results.
    """
    aggregate_id: str
    changed: bool
    events: list[DomainEvent]
    new_state: str | None

    def __post_init__(self):
        if self.changed is False and self.events:
            raise ValueError("If 'changed' is False, 'events' must be empty.")
