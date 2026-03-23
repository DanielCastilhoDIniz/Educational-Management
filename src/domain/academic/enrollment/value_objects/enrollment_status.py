from enum import StrEnum


class EnrollmentState(StrEnum):
    """
    possible Enrollment states:
    ACTIVE, SUSPENDED, CONCLUDED, CANCELLED
    """
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    CONCLUDED = 'concluded'
    CANCELLED = 'cancelled'
