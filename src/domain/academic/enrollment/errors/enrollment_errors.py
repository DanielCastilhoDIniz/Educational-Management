

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
        super().__init__(message)

        self.code = code
        self.message = message
        self.details = details


class InvalidStateTransitionError(DomainError):
    ...


class EnrollmentNotActiveError(DomainError):
    ...


class EnrollmentAlreadyFinalError(DomainError):
    ...


class ConclusionNotAllowedError(DomainError):
    ...


class JustificationRequiredError(DomainError):
    ...
