from __future__ import annotations

from typing import Protocol

from domain.academic.enrollment.entities.enrollment import Enrollment


class EnrollmentRepository(Protocol):
    """
    Port (contract) for Enrollment persistence.

    Responsibilities:
    - Retrieve an Enrollment aggregate by id.
    - Persist an existing Enrollment aggregate state.

    Non-responsibilities:
    - Must not enforce business rules (domain does).
    - Must not emit domain events (application pulls them).
    """

    def get_by_id(self, enrollment_id: str) -> Enrollment | None:
        """
        Return the Enrollment aggregate for the given id, or None if no record exists.

        Implementations must reconstruct a semantically valid aggregate from
        persisted data and must not silently mask persistence/mapping
        inconsistencies as "not found".
        """
        ...

    def save(self, enrollment: Enrollment) -> int:
        """
        Persist the current state of an existing Enrollment aggregate and return
        the new persisted version.

        Implementations must treat the aggregate version as the expected origin
        version, enforce optimistic concurrency control, and fail explicitly on:
        - missing records for update
        - concurrency conflicts
        - data integrity violations
        - unexpected persistence failures
        """
        ...

    def create(self, enrollment: Enrollment) -> int:
        """
            Persists a new Enrollment aggregate.

            This method is strictly for creating a new enrollment record. It must 
            not be used to update an existing aggregate. Final uniqueness is 
            guaranteed by the persistence layer (e.g., database constraints) at 
            the moment of insertion to prevent race conditions.

            Returns:
                int: The initial version of the newly persisted enrollment.

            Raises:
                EnrollmentDuplicationError: Raised when the persistence layer confirms a
                duplication, either by an explicit ID or by the business key 
                    (institution, student, class, and period).
                EnrollmentTechnicalPersistenceError: Raised when technical failures occur during 
                    communication with the persistence layer or when unexpected 
                    integrity violations (such as missing foreign keys or null 
                    constraint violations) are encountered.
            """
        ...
