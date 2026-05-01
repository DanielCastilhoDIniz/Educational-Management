
from __future__ import annotations

from typing import Protocol

from domain.identity.user.entities.user import User


class UserRepository(Protocol):
    """
    Port (contract) for User persistence.

    Responsibilities:
    - Retrieve a User aggregate by id.
    - Persist an existing User aggregate state.

    Non-responsibilities:
    - Must not enforce business rules (domain does).
    - Must not emit domain events (application pulls them).
    """

    def get_by_id(self, user_id: str) -> User | None:
        """
        Return the User aggregate for the given id, or None if no record exists.

        Implementations must reconstruct a semantically valid aggregate from
        persisted data and must not silently mask persistence/mapping
        inconsistencies as "not found".
        """
        ...

    def save(self, user: User) -> int:
        """
        Persist the current state of an existing User aggregate and return
        the new persisted version. 
        """
        ...


    def create(self, user: User) -> int:
        """
        Persists a new User aggregate.

        this method is strictly for creating a new user record. It must 
        not be used to update an existing aggregate. Final uniqueness is 
        guaranteed by the persistence layer (e.g., database constraints)
        at the moment of insertion to prevent race conditions.

        Returns:
            int: The initial version of the newly persisted user.
            
        Raises:
            UserDuplicationError: Raised when the persistence layer confirms a
            duplication, either by an explicit ID or by the business key 
                legal_identity=LegalIdentity(identity_type, identity_number, identity_issuer)).
            UserTechnicalPersistenceError: Raised when technical failures occur during 
                communication with the persistence layer
                or when unexpected integrity violations (such as missing foreign keys or null 
                constraint violations) are encountered.

        """
        ...