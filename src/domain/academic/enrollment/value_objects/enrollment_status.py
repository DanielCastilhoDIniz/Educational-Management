from enum import Enum


class EnrollmentState(Enum):
    """
    possible Enrollment states:
    ACTIVE, SUSPENDED, CONCLUDED, CANCELLED
    """
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    CONCLUDED = 'concluded'
    CANCELLED = 'cancelled'
