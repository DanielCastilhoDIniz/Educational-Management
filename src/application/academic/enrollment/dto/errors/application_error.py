from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, kw_only=True)
class ApplicationError:
    """
Represents a *serializable* and *stable* error payload returned by the Application Layer.

This project follows the "Contract A" rule:
- Application Services do not raise exceptions for expected failures.
- Instead, they return an ApplicationResult with `success=False` and an `ApplicationError`.

Fields
------
code:
    Stable, machine-readable identifier used for:
    - mapping to HTTP status codes (Presentation/DRF),
    - client-side handling,
    - analytics and monitoring.
    Examples: "ENROLLMENT_NOT_FOUND", "INVALID_STATE_TRANSITION".

message:
    Human-readable explanation of the failure, safe to display to operators/users
    (do not include stack traces or sensitive internal details).

details:
    Optional structured metadata to help debugging and clients, e.g.:
    {"from_state": "CANCELLED", "to_state": "CONCLUDED"}.

Notes
-----
- This is a DTO (data object), not an Exception.
- It must remain immutable and JSON-serializable.
"""

    code: str
    message: str
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}" \
               f", message={self.message!r}, details={self.details!r})"