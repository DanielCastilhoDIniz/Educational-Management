from __future__ import annotations

from typing import Any

from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.errors.domain_error_mapper import to_application_error
from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from domain.academic.enrollment.errors.enrollment_errors import DomainError
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def build_not_found_result(*, enrollment_id: str, action: str) -> ApplicationResult:
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
        current_state: str,
        message: str,
        err: Exception,
) -> ApplicationResult:
    return ApplicationResult(
        aggregate_id=enrollment_id,
        success=False,
        changed=False,
        domain_events=(),
        new_state=None,
        error=ApplicationError(
            code=ErrorCodes.UNEXPECTED_ERROR,
            message=message,
            details={
                "aggregate_id": enrollment_id,
                "action": action,
                "current_state": current_state,
                "exception_type": err.__class__.__name__,
                "exception_message": str(err),
            }
        )
    )


def build_state_integrity_result(
        *,
        enrollment_id: str,
        action: str,
        previous_state: str,
        current_state: str,
        reason: str,
        message: str,
) -> ApplicationResult:
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
                "previous_state": previous_state,
                "current_state": current_state,
                "reason": reason,
            }
        )
    )


def build_no_change_result(*, enrollment_id: str) -> ApplicationResult:
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
        enrollment: Any,
        enrollment_id: str,
        action: str,
        previous_state: EnrollmentState,
        persistence_failure_message: str,
        event_without_state_change_message: str,
        state_changed_without_event_message: str,
) -> ApplicationResult:
    state_changed = enrollment.state != previous_state
    events_snapshot = tuple(enrollment.peek_domain_events())

    if not state_changed:
        if events_snapshot:
            return build_state_integrity_result(
                enrollment_id=enrollment_id,
                action=action,
                previous_state=previous_state.value,
                current_state=enrollment.state.value,
                reason="event_without_state_change",
                message=event_without_state_change_message,
            )
        return build_no_change_result(enrollment_id=enrollment_id)

    if not events_snapshot:
        return build_state_integrity_result(
            enrollment_id=enrollment_id,
            action=action,
            previous_state=previous_state.value,
            current_state=enrollment.state.value,
            reason="state_changed_without_event",
            message=state_changed_without_event_message,
        )

    try:
        repo.save(enrollment)
    except Exception as err:
        return build_persistence_failure_result(
            enrollment_id=enrollment_id,
            action=action,
            current_state=enrollment.state.value,
            message=persistence_failure_message,
            err=err,
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
