import uuid
from datetime import datetime, timezone

from .constants import ACADEMIC_ENROLLMENT_TRANSITION_NS


def _normalize_occurred_at(dt: datetime) -> datetime:
    """Normalize the occurred_at timestamp to UTC timezone."""

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def make_transition_id(
    *,
    enrollment_id: uuid.UUID,
    action: str,
    from_state: str,
    to_state: str,
    occurred_at: datetime,
    actor_id: str,
    justification: str | None,
) -> uuid.UUID:
    """
        Generate a deterministic UUID for an enrollment state transition.
        The UUID is based on the enrollment ID, action, from/to states, timestamp, actor, and justification.
        This ensures that the same transition will always yield the same UUID, which is useful for id
        empotency and traceability.

        Parameters:
        - enrollment_id: The UUID of the enrollment undergoing the transition.
        - action: The action that triggered the transition.
        - from_state: The state before the transition.
        - to_state: The state after the transition.
        - occurred_at: The timestamp when the transition occurred.
        - actor_id: The ID of the actor performing the transition.
        - justification: Optional justification for the transition.

        Returns:
        - A deterministic UUID representing the transition.
    """

    occurred_at = _normalize_occurred_at(occurred_at)
    just = (justification or "").strip()

    fingerprint = (
        f"enrollment:{enrollment_id}|"
        f"action:{action}|"
        f"from:{from_state}|"
        f"to:{to_state}|"
        f"at:{occurred_at.isoformat()}|"
        f"actor:{actor_id}|"
        f"just:{just}"
    )

    return uuid.uuid5(ACADEMIC_ENROLLMENT_TRANSITION_NS, fingerprint)
