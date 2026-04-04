from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from domain.academic.enrollment.errors.enrollment_errors import (
    ConclusionNotAllowedError,
    DomainError,
    EnrollmentNotActiveError,
    InvalidStateTransitionError,
    JustificationRequiredError,
)
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def to_application_error(
        *,
        err: DomainError,
        aggregate_id: str,
        action: str,
        current_state: EnrollmentState | None = None
) -> ApplicationError:
    base_details = {
            "aggregate_id": aggregate_id,
            "action": action,
            "current_state": current_state.value if current_state else None,
            "domain_code": err.code,
        }
    if isinstance(err, EnrollmentNotActiveError):
        details = dict(err.details or {})
        details.update(base_details)
        return ApplicationError(
            code=ErrorCodes.ENROLLMENT_NOT_ACTIVE,
            message=err.message,
            details=details,
        )

    if isinstance(err, JustificationRequiredError):
        details = dict(err.details or {})
        details.update(base_details)
        return ApplicationError(
            code=ErrorCodes.JUSTIFICATION_REQUIRED,
            message=err.message,
            details=details,
        )
    if isinstance(err, ConclusionNotAllowedError):
        details = dict(err.details or {})
        details.update(base_details)
        return ApplicationError(
            code=ErrorCodes.CONCLUSION_NOT_ALLOWED,
            message=err.message,
            details=details,
        )
    if isinstance(
        err, InvalidStateTransitionError
        ): 

        details = dict(err.details or {})
        details.update(base_details)
        return ApplicationError(
            code=ErrorCodes.INVALID_STATE_TRANSITION,
            message=err.message,
            details=details,
        )
    # Fallback (required): never return ApplicationError() empty
    details = dict(err.details or {})
    details.update(base_details)
    details.update({"domain_error": err.__class__.__name__})

    return ApplicationError(
        code=ErrorCodes.STATE_INTEGRITY_VIOLATION,
        message=err.message,
        details=details,
    )
