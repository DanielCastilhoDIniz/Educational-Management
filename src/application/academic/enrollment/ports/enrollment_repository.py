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
        Persist a new Enrollment aggregate and return the new persisted version.
        Implementations must fail explicitly on:
        - attempts to create with an existing id
        - data integrity violations
        - unexpected persistence failures
        
        """
        ...
