from __future__ import annotations

from dataclasses import dataclass, field
from domain.academic.enrollment.errors.enrollment_errors import DomainError


@dataclass(frozen=True)
class ConclusionVerdict:
    """
    Represents the conclusion verdict for an enrollment (Value Object).

    Invariants:
    - is_allowed=True  => reasons must be empty
    - is_allowed=False => requires_justification must be False
    - is_allowed=False => reasons must not be empty
    """
    is_allowed: bool = True
    reasons: list[str] = field(default_factory=list)
    requires_justification: bool = False

    def __post_init__(self) -> None:
        if self.is_allowed:
            if self.reasons:
                raise DomainError(
                    code="invalid_verdict_state",
                    message="Allowed verdict cannot contain reasons.",
                    details={"reasons": self.reasons},
                )
        else:
            if self.requires_justification:
                raise DomainError(
                    code="invalid_verdict_state",
                    message="Denied verdict cannot require justification.",
                    details={"requires_justification": self.requires_justification},
                )
            if not self.reasons:
                raise DomainError(
                    code="invalid_verdict_state",
                    message="Denied verdict must contain at least one reason.",
                    details={"reasons": self.reasons},
                )

    @classmethod
    def allowed(cls, requires_justification: bool = False) -> 'ConclusionVerdict':
        """Create success verdict with justification requirement."""
        return cls(is_allowed=True, reasons=[], requires_justification=requires_justification)

    @classmethod
    def denied(cls, reasons: list[str]) -> 'ConclusionVerdict':
        """Create a denied verdict with defensive-copied reasons."""
        return cls(is_allowed=False, reasons=list(reasons), requires_justification=False)
