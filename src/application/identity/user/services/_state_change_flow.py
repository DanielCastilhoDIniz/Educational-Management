"""Shared builders for User application services.

These helpers keep the three state-change use cases aligned around the same
result contract:
- expected failures are returned as ``ApplicationResult(success=False)``
- successful changes are persisted before pending events are cleared
- inconsistencies between state mutation and event emission are surfaced as
  ``STATE_INTEGRITY_VIOLATION``
"""

from __future__ import annotations

from typing import Protocol, cast

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.dto.results import ApplicationResult
from application.shared.application_error import ApplicationError
from application.shared.errors.error_codes import SharedErrorCodes
from domain.identity.user.entities.user import User
from domain.identity.user.value_objects.user_state import UserState
from domain.shared.domain_error import DomainError
from domain.shared.domain_event import DomainEvent


class UserLike(Protocol):
    """
    Subset of the user aggregate interface required by the state change flow.
    This allows the service to work with both the full aggregate and a simpler
    stateful wrapper used for validation in scripted cases.
    """

def build_persistence_failure_result(
        *,
        user_id: str,
        action: str,
        current_state: UserState,
        code: ErrorCodes | SharedErrorCodes = SharedErrorCodes.UNEXPECTED_ERROR,
        message: str,
        err: Exception,
) -> ApplicationResult:
    """Return a generic infrastructure failure without leaking an exception."""
    return ApplicationResult(
        aggregate_id=user_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=ApplicationError(
            code=code,
            message=message,
            details={
                "aggregate_id": user_id,
                "action": action,
                "current_state": current_state.value,
                "exception_type": err.__class__.__name__,
                "exception_message": str(err),
            }
        )
    )
