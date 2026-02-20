

class DomainError(Exception):
    """
        Raise errors message in domain layer
    """

    code: str
    message: str
    details: dict[str, object] | None = None

    def __init__(
            self, code: str,
            message: str,
            details: dict[str, object] | None = None,
            ) -> None:

        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}" \
               f", message={self.message!r}, details={self.details!r})"


class InvalidStateTransitionError(DomainError):
    """Raised when a state transition is logically impossible (e.g. Active -> Active)."""
    ...


class IrreversibleStateError(DomainError):
    """
    Raised when attempting to change a terminal state.
    Strictly implements DOMAIN_RULES Rule 4.2: 'CANCELADA' or 'CONCLUÍDA' cannot return to 'ATIVA'.
    """
    ...


class EnrollmentNotActiveError(DomainError):
    """Raised when an operation requires an ACTIVE state but the enrollment is in another state."""
    ...


class EnrollmentAlreadyFinalError(DomainError):
    """Raised when trying to modify an aggregate that has reached a terminal state."""
    ...


class ConclusionNotAllowedError(DomainError):
    """Raised when pedagogical or institutional criteria for conclusion are not met (Rule 5.4)."""
    ...


class JustificationRequiredError(DomainError):
    """Raised when an action (like cancellation or suspension) lacks a mandatory justification."""
    ...
