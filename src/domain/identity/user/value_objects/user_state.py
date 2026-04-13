from enum import StrEnum


class UserState(StrEnum):
    """
    ADR032: possible Users states:
            PENDING, ACTIVE, SUSPENDED, INACTIVE
    """
    PENDING = 'pending'
    ACTIVE = 'active'
    SUSPENDED = 'suspended'
    INACTIVE = 'inactive'