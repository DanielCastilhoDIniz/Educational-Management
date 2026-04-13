from domain.shared.domain_error import DomainError


class UserRequiredGuardianIDError(DomainError):
    """
        Raised when trying to create a new user without a guardian.
    """
    ...
class JustificationRequiredError(DomainError):
    """
    Raised when a state transition requires a justification that was not provided.
    """
    ...
class InvalidStateTransitionError(DomainError):
    """
    Raised when a state transition is logically impossible (e.g. Active -> Active).
    """
    ...

