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
from application.identity.user.errors.domain_error_mapper import to_application_error
from application.identity.user.errors.persistence_errors import (
    ConcurrencyConflictError,
    UserPersistenceNotFoundError,
    UserTechnicalPersistenceError,
)
from application.identity.user.ports.user_repository import UserRepository
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
    state: UserState
    def pull_domain_events(self) -> list[DomainEvent]: ...
    def peek_domain_events(self) -> list[DomainEvent]: ...


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

def build_domain_failure_result(
        *,
        user_id: str,
        current_state: UserState,
        action: str,
        err: DomainError,
) -> ApplicationResult:
    """Translate a domain exception into the stable application error contract."""
    return ApplicationResult(
        aggregate_id=user_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=to_application_error(
            err=err,
            aggregate_id=user_id,
            action=action,
            current_state=current_state
        )
    )

def build_not_found_result(
    *,
    user_id:str,
    action: str,
) -> ApplicationResult:
    """Build the standard failure payload for a missing user aggregate."""

    return ApplicationResult(
            aggregate_id=user_id,
            success=False,
            changed=False,
            new_state=None,
            error=ApplicationError(
                code=ErrorCodes.USER_NOT_FOUND,
                message=f"User with id {user_id} not found.",
                details={
                    "aggregate_id": user_id,
                    "action": action,
                    "current_state": None,
                }   
            )
    )

def build_state_integrity_result(
        *,
        user_id: str,
        action: str,
        previous_state: UserState,
        current_state: UserState,
        reason: str,
        message: str,
    ) -> ApplicationResult:
    """Report an impossible state/event combination detected by the service."""
     
    return ApplicationResult(
         aggregate_id=user_id,
         success=False,
         changed=False,
         domain_events=(),
         new_state=None,
         error=ApplicationError(
              code=ErrorCodes.STATE_INTEGRITY_VIOLATION,
              message=message,
              details={
                   "aggregate": user_id,
                   "action":action,
                   "previous_state": previous_state.value,
                   "current_state" : current_state.value,
                   "reason": reason,
              }
         )
    )
def build_no_change_result(*, user_id: str) -> ApplicationResult:
    """Return the canonical no-op result for idempotent commands."""
    return ApplicationResult(
        aggregate_id=user_id,
        changed=False,
        success=True,
        domain_events=(),
        new_state=None,
        error=None
    )
    
def finalize_state_change(
        *,
        repo: UserRepository,
        user: UserLike,
        user_id: str,
        action: str,
        previous_state: UserState,
        persistence_failure_message: str,
        event_without_state_change_message: str,
        state_changed_without_event_message: str,
) -> ApplicationResult:
    """Finalize a successful domain command under the application contract. 
    Rules enforced here:
    - no state change + pending events => integrity violation
    - state change + no pending events => integrity violation
    - on persistence failure, events remain buffered in the aggregate
    - on success, the service returns an event snapshot and then clears the
      aggregate buffer
    """
    state_changed = user.state != previous_state
    events_snapshot = tuple(user.peek_domain_events())

    if not state_changed:
        if events_snapshot:
            return build_state_integrity_result(
                user_id=user_id,
                action=action,
                previous_state=previous_state,
                current_state=user.state,
                reason="event_without_state_change",
                message=event_without_state_change_message,               
            )
        return build_no_change_result(user_id=user_id)
    
    if not events_snapshot:
        return build_state_integrity_result(
            user_id=user_id,
            action=action,
            previous_state=previous_state,
            current_state=user.state,
            reason="state_changed_without_event",
            message=state_changed_without_event_message,               
        )
    try:
        repo.save(cast(User, user))
    except ConcurrencyConflictError as e:
        return build_persistence_failure_result(
            user_id=user_id,
            action=action,
            current_state=user.state,
            code=ErrorCodes.CONCURRENCY_CONFLICT,
            message=persistence_failure_message,
            err=e,
        )
    except UserPersistenceNotFoundError as e:
        return build_persistence_failure_result(
            user_id=user_id,
            action=action,
            current_state=user.state,
            code=cast(ErrorCodes, e.code),
            message=persistence_failure_message,
            err=e,            
        )
    except UserTechnicalPersistenceError as e:
        return build_persistence_failure_result(
            user_id=user_id,
            action=action,
            current_state=user.state,
            code=cast(ErrorCodes, e.code),
            message=persistence_failure_message,
            err=e,            
        )
    
    user.pull_domain_events()

    return ApplicationResult(
        aggregate_id=user_id,
        changed=True,
        success=True,
        domain_events=events_snapshot,
        new_state=user.state,
        error=None
    )