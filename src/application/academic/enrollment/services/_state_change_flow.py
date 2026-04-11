"""Shared builders for enrollment application services.

These helpers keep the three state-change use cases aligned around the same
result contract:
- expected failures are returned as ``ApplicationResult(success=False)``
- successful changes are persisted before pending events are cleared
- inconsistencies between state mutation and event emission are surfaced as
  ``STATE_INTEGRITY_VIOLATION``
"""

from __future__ import annotations

from typing import Protocol, cast

from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.errors.domain_error_mapper import to_application_error
from application.academic.enrollment.errors.persistence_errors import (
    ConcurrencyConflictError,
    EnrollmentPersistenceNotFoundError,
    EnrollmentTechnicalPersistenceError,
)
from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.errors.enrollment_errors import DomainError
from domain.academic.enrollment.events.enrollment_events import DomainEvent
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


class EnrollmentLike(Protocol):
    """Subset of the Enrollment aggregate interface required by the state change flow.
     This allows the service to work with both the full aggregate and a simpler
     stateful wrapper used for validation in scripted cases.

    """
    state: EnrollmentState
    def pull_domain_events(self) -> list[DomainEvent]: ...
    def peek_domain_events(self) -> list[DomainEvent]: ...

def build_not_found_result(*, enrollment_id: str, action: str) -> ApplicationResult:
    """Build the standard failure payload for a missing enrollment aggregate."""
    return ApplicationResult(
        aggregate_id=enrollment_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=ApplicationError(
            code=ErrorCodes.ENROLLMENT_NOT_FOUND,
            message=f"Enrollment with id {enrollment_id} not found.",
            details={
                "aggregate_id": enrollment_id,
                "action": action,
                "current_state": None,
            }
        )
    )


def build_domain_failure_result(
        *,
        enrollment_id: str,
        current_state: EnrollmentState,
        action: str,
        err: DomainError,
) -> ApplicationResult:
    """Translate a domain exception into the stable application error contract."""
    return ApplicationResult(
        aggregate_id=enrollment_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=to_application_error(
            err=err,
            aggregate_id=enrollment_id,
            action=action,
            current_state=current_state
        )
    )


def build_persistence_failure_result(
        *,
        enrollment_id: str,
        action: str,
        current_state: EnrollmentState,
        code: ErrorCodes = ErrorCodes.UNEXPECTED_ERROR,    
        message: str,
        err: Exception,
) -> ApplicationResult:
    """Return a generic infrastructure failure without leaking an exception."""
    return ApplicationResult(
        aggregate_id=enrollment_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=ApplicationError(
            code=code,
            message=message,
            details={
                "aggregate_id": enrollment_id,
                "action": action,
                "current_state": current_state.value,
                "exception_type": err.__class__.__name__,
                "exception_message": str(err),
            }
        )
    )

def build_concurrency_conflict_result(
        *,
        enrollment_id: str,
        action: str,
        current_state: EnrollmentState,
        message: str,
        err: ConcurrencyConflictError,
) -> ApplicationResult:
    """Return a concurrency conflict failure without leaking an exception."""
    return ApplicationResult(
        aggregate_id=enrollment_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=ApplicationError(
            code=ErrorCodes.CONCURRENCY_CONFLICT,
            message=message,
            details={
                "aggregate_id": enrollment_id,
                "action": action,
                "current_state": current_state.value,
                "expected_version": (err.details or {}).get("expected_version"),
                "persisted_version": (err.details or {}).get("persisted_version"),
                "exception_type": err.__class__.__name__,
                "exception_message": str(err),
            }
        )
    )


def build_state_integrity_result(
        *,
        enrollment_id: str,
        action: str,
        previous_state: EnrollmentState,
        current_state: EnrollmentState,
        reason: str,
        message: str,
) -> ApplicationResult:
    """Report an impossible state/event combination detected by the service."""
    return ApplicationResult(
        aggregate_id=enrollment_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=ApplicationError(
            code=ErrorCodes.STATE_INTEGRITY_VIOLATION,
            message=message,
            details={
                "aggregate_id": enrollment_id,
                "action": action,
                "previous_state": previous_state.value,
                "current_state": current_state.value,
                "reason": reason,
            }
        )
    )


def build_no_change_result(*, enrollment_id: str) -> ApplicationResult:
    """Return the canonical no-op result for idempotent commands."""
    return ApplicationResult(
        aggregate_id=enrollment_id,
        changed=False,
        success=True,
        domain_events=(),
        new_state=None,
        error=None
    )


def finalize_state_change(
        *,
        repo: EnrollmentRepository,
        enrollment: EnrollmentLike,
        enrollment_id: str,
        action: str,
        previous_state: EnrollmentState,
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
    state_changed = enrollment.state != previous_state
    events_snapshot = tuple(enrollment.peek_domain_events())

    if not state_changed:
        if events_snapshot:
            return build_state_integrity_result(
                enrollment_id=enrollment_id,
                action=action,
                previous_state=previous_state,
                current_state=enrollment.state,
                reason="event_without_state_change",
                message=event_without_state_change_message,
            )
        return build_no_change_result(enrollment_id=enrollment_id)

    if not events_snapshot:
        return build_state_integrity_result(
            enrollment_id=enrollment_id,
            action=action,
            previous_state=previous_state,
            current_state=enrollment.state,
            reason="state_changed_without_event",
            message=state_changed_without_event_message,
        )

    try:
        repo.save(cast(Enrollment, enrollment))
    except ConcurrencyConflictError as e:
        return build_concurrency_conflict_result(
            enrollment_id=enrollment_id,
            action=action,
            current_state=enrollment.state,
            message=persistence_failure_message,
            err=e,
        )
    except EnrollmentPersistenceNotFoundError as e:
        return build_persistence_failure_result(
            enrollment_id=enrollment_id,
            action=action,
            current_state=enrollment.state,
            message=persistence_failure_message,
            code=ErrorCodes.DATA_INTEGRITY_ERROR,
            err=e,
        )
    except EnrollmentTechnicalPersistenceError as e:
        return build_persistence_failure_result(
            enrollment_id=enrollment_id,
            action=action,
            current_state=enrollment.state,
            message=persistence_failure_message,
            code=ErrorCodes.DATABASE_ERROR,
            err=e,
        )

    enrollment.pull_domain_events()

    return ApplicationResult(
        aggregate_id=enrollment_id,
        changed=True,
        success=True,
        domain_events=events_snapshot,
        new_state=enrollment.state,
        error=None
    )
