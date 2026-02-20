from __future__ import annotations
from dataclasses import dataclass

from domain.academic.enrollment.events.enrollment_events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ApplicationResult:
    """
    Base class for application results.
    """
    aggregate_id: str
    success: bool
    changed: bool
    domain_events: tuple[DomainEvent, ...]
    new_state: str | None
    error: Exception | None = None

    def __post_init__(self):
        if not self.changed and self.events:
            raise ValueError("If 'changed' is False, 'events' must be empty.")

        if self.changed and self.new_state is None:
            raise ValueError("If 'changed' is True, 'new_state' is required.")

        if not self.changed and self.new_state is not None:
            raise ValueError("If 'changed' is False, 'new_state' must be None.")
