from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.shared.application_error import ApplicationError
from domain.identity.user.errors.user_errors import (
    DomainError,
    InvalidStateTransitionError,
    JustificationRequiredError,
    UserRequiredGuardianIDError,
)
from domain.identity.user.value_objects.user_state import UserState


def to_application_error(
        *,
        err: DomainError,
        aggregate_id: str,
        action: str,
        current_state: UserState | None = None
) -> ApplicationError:
    base_details = {
            "aggregate_id": aggregate_id,
            "action": action,
            "current_state": current_state.value if current_state else None,
            "domain_code": err.code,
        }
    if isinstance(err, InvalidStateTransitionError):
        details = dict(err.details or {})
        details.update(base_details)
        return ApplicationError(
            code=ErrorCodes.INVALID_STATE_TRANSITION,
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
    if isinstance(err, UserRequiredGuardianIDError):
        details = dict(err.details or {})
        details.update(base_details)
        return ApplicationError(
            code=ErrorCodes.USER_REQUIRED_GUARDIAN,
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
