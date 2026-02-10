from __future__ import annotations

from typing import Protocol

from domain.academic.enrollment.entities.enrollment import Enrollment


class EnrollmentRepository(Protocol):
    """
    Port (contract) for Enrollment persistence.

    Responsibilities:
    - Retrieve an Enrollment aggregate by id.
    - Persist an Enrollment aggregate state.

    Non-responsibilities:
    - Must not enforce business rules (domain does).
    - Must not emit domain events (application pulls them).
    """

    def get_by_id(self, enrollment_id: str) -> Enrollment | None:
        """Return Enrollment if found, otherwise None."""
        ...

    def save(self, enrollment: Enrollment) -> None:
        """Persist the current state of the aggregate."""
        ...

