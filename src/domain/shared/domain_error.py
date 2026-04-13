class DomainError(Exception):
    """Base class for all domain errors.

    Represents a violation of a business rule or invariant in the domain layer.
    All domain-specific errors should subclass this.
    """

    code: str
    message: str
    details: dict[str, object] | None = None

    def __init__(
            self,
            code: str,
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
        return (
            f"{self.__class__.__name__}(code={self.code!r}"
            f", message={self.message!r}, details={self.details!r})"
        )
