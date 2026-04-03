class ApplicationPersistenceError(Exception):
    """Base exception for persistence-related errors in the enrollment application."""
    code: str
    message: str

    def __init__(
            self, code: str,
            message: str,
            details: dict[str, object] | None = None
            ) -> None:

        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}"\
               f", message={self.message!r}, details={self.details!r}"


class EnrollmentPersistenceNotFoundError(ApplicationPersistenceError):
    """
        Raised when an enrollment_id cannot be found
        during persistence execution.
    """


class ConcurrencyConflictError(ApplicationPersistenceError):
    """
    Raised when a version mismatch occurs during persistence,
    indicating that the aggregate was modified by another process.
    """

class EnrollmentDuplicationError(ApplicationPersistenceError):
    """
    Raised when an attempt is made to create an enrollment that already exists,
    violating a uniqueness constraint.
    """

class EnrollmentCreationError(ApplicationPersistenceError):
    """
    Raised when an unexpected error occurs during the creation of an enrollment,
    such as a database failure or other infrastructure issue.
    """