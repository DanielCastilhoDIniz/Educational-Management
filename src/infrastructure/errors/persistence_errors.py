class InfrastructureError(Exception):
    """Base class for infrastructure layer errors."""
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


class EnrollmentDuplicationInfrastructureError (InfrastructureError):
    """Raised when an attempt is made to create a duplicate enrollment.
        helper for EnrollmentDuplicationError in the application layer.    
    """