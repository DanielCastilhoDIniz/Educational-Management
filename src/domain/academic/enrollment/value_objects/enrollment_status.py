from enum import Enum


class EnrollmentState(Enum):
    """
    possible Enrollment states”
    """
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
