

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
    """
        Raise errors message in domain layer,
        when state transition is invalid
    """
    ...


class EnrollmentNotActiveError(DomainError):
    """
        Raise errors message in domain layer,
        when enrollment is not active.
    """

    ...


class EnrollmentAlreadyFinalError(DomainError):
    """
        Raise errors message in domain layer,
        when enrollment is already final.
    """

    ...


class ConclusionNotAllowedError(DomainError):
    """
        Raise errors message in domain layer,
        when conclusion is no allowed.
    """
    ...


class JustificationRequiredError(DomainError):
    """
        Raise errors message in domain layer,
        when justification is required.
    """

    ...
