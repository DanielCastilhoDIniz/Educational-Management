from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for all domain events.

    Represents an immutable fact that occurred in the business domain.
    All events are frozen (immutable) and use keyword-only arguments for clarity.

    Attributes:
        aggregate_id: Unique identifier of the affected aggregate root.
        occurred_at: Date and time when the event actually occurred.
        event_id: Globally unique identifier of the event (UUID v4).
    """

    aggregate_id: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    event_id: str = field(default_factory=lambda: str(uuid4()))
