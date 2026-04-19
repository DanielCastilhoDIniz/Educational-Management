class ApplicationPersistenceError(Exception):
    """Base exception for persistence-related errors in the enrollment application.
       code tipada como str para permitir flexibilidade na definição de códigos de erro 
       específicos por cenário, sem amarrar a um enum específico. O código deve ser 
       escolhido de forma consistente para facilitar o tratamento e a análise dos erros em toda a aplicação.
       use o padrão de tipo estrito: cast(ErrorCodes, e.code) no call site"""
    
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
               f", message={self.message!r}, details={self.details!r})"


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


class EnrollmentTechnicalPersistenceError(ApplicationPersistenceError):
    """
    Raised for unexpected technical errors during enrollment persistence operations,
    such as database connectivity issues or other infrastructure failures.
    """