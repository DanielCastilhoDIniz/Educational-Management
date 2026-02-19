from dataclasses import dataclass, field
from typing import cast


@dataclass(frozen=True)
class ConclusionVerdict:
    """
    Represents the conclusion verdict for an enrollment (V.O - Value Object).
    This class encapsulates the logic to determine if an enrollment can be concluded,
    and if not, the reasons why it cannot be concluded.
    It also indicates whether a justification is required for the conclusion decision.
    """
    is_allowed: bool = True
    reasons: list[str] = field(default_factory=lambda: cast(list[str], []))
    requires_justification: bool = False
