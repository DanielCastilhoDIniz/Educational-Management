from dataclasses import dataclass, field
from typing import cast


@dataclass(frozen=True)
class ConclusionVerdict:
    """
    enrollment verdict
    """
    is_allowed: bool = True
    reasons: list[str] = field(default_factory=lambda: cast(list[str], []))
    requires_justification: bool = False
