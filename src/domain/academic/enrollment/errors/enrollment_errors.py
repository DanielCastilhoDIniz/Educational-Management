from domain.shared.domain_error import DomainError


class InvalidStateTransitionError(DomainError):
    """Raised when a state transition is logically impossible (e.g. Active -> Active)."""
    ...


class EnrollmentNotActiveError(DomainError):
    """Raised when an operation requires an ACTIVE state but the enrollment is in another state."""
    ...


class ConclusionNotAllowedError(DomainError):
    """Raised when pedagogical or institutional criteria for conclusion are not met (Rule 5.4)."""
    ...


class JustificationRequiredError(DomainError):
    """Raised when an action (like cancellation or suspension) lacks a mandatory justification."""
    ...
