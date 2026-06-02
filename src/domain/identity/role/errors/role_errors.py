from domain.shared.domain_error import DomainError


class InvalidStateTransitionError(DomainError):
    """
    Raised when a state transition is logically impossible (e.g. Active -> Active).
    """
    ...

class CodeRequiredError(DomainError):
    """
        Raised when 
    """
    ...

class NameRequiredError(DomainError):
    """
    """
    ...