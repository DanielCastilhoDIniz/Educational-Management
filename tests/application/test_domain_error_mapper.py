import pytest

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.errors.domain_error_mapper import to_application_error
from domain.academic.enrollment.errors.enrollment_errors import (
    ConclusionNotAllowedError,
    DomainError,
    EnrollmentAlreadyFinalError,
    EnrollmentNotActiveError,
    InvalidStateTransitionError,
    IrreversibleStateError,
    JustificationRequiredError,
)
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def test_maps_enrollment_not_active_error() -> None:
    err = EnrollmentNotActiveError(
        code="enrollment_not_active",
        message="Enrollment must be active.",
        details={
            "attempted_action": "conclude",
            "required_state": EnrollmentState.ACTIVE.value,
        },
    )

    result = to_application_error(
        err=err,
        aggregate_id="enr-1",
        action="conclude",
        current_state=EnrollmentState.SUSPENDED,
    )

    assert result.code == ErrorCodes.ENROLLMENT_NOT_ACTIVE
    assert result.message == err.message
    assert result.details is not None
    assert result.details["aggregate_id"] == "enr-1"
    assert result.details["action"] == "conclude"
    assert result.details["current_state"] == EnrollmentState.SUSPENDED.value
    assert result.details["domain_code"] == "enrollment_not_active"
    assert result.details["attempted_action"] == "conclude"
    assert result.details["required_state"] == EnrollmentState.ACTIVE.value


def test_maps_justification_required_error() -> None:
    err = JustificationRequiredError(
        code="justification_required",
        message="Justification is required.",
        details={
            "policy": "verdict_requires_justification",
            "attempted_action": "conclude",
        },
    )

    result = to_application_error(
        err=err,
        aggregate_id="enr-1",
        action="conclude",
        current_state=EnrollmentState.ACTIVE,
    )

    assert result.code == ErrorCodes.JUSTIFICATION_REQUIRED
    assert result.message == err.message
    assert result.details is not None
    assert result.details["aggregate_id"] == "enr-1"
    assert result.details["action"] == "conclude"
    assert result.details["current_state"] == EnrollmentState.ACTIVE.value
    assert result.details["domain_code"] == "justification_required"
    assert result.details["policy"] == "verdict_requires_justification"
    assert result.details["attempted_action"] == "conclude"


def test_maps_conclusion_not_allowed_error() -> None:
    err = ConclusionNotAllowedError(
        code="conclusion_not_allowed",
        message="Conclusion is not allowed by policy.",
        details={
            "reasons": ("pending grades",),
            "attempted_action": "conclude",
        },
    )

    result = to_application_error(
        err=err,
        aggregate_id="enr-1",
        action="conclude",
        current_state=EnrollmentState.ACTIVE,
    )

    assert result.code == ErrorCodes.CONCLUSION_NOT_ALLOWED
    assert result.message == err.message
    assert result.details is not None
    assert result.details["aggregate_id"] == "enr-1"
    assert result.details["action"] == "conclude"
    assert result.details["current_state"] == EnrollmentState.ACTIVE.value
    assert result.details["domain_code"] == "conclusion_not_allowed"
    assert result.details["reasons"] == ("pending grades",)
    assert result.details["attempted_action"] == "conclude"


@pytest.mark.parametrize(
    ("error_type", "details"),
    [
        (
            InvalidStateTransitionError,
            {
                "attempted_action": "reactivate",
                "allowed_from_states": [EnrollmentState.SUSPENDED.value],
            },
        ),
        (
            IrreversibleStateError,
            {
                "attempted_action": "reactivate",
                "allowed_from_states": [EnrollmentState.SUSPENDED.value],
            },
        ),
        (
            EnrollmentAlreadyFinalError,
            {
                "attempted_action": "cancel",
                "allowed_from_states": [EnrollmentState.ACTIVE.value],
            },
        ),
    ],
)
def test_maps_transition_related_errors_to_invalid_state_transition(
    error_type: type[DomainError],
    details: dict[str, object],
) -> None:
    err = error_type(
        code="invalid_state_transition",
        message="Transition is not allowed.",
        details=details,
    )

    result = to_application_error(
        err=err,
        aggregate_id="enr-1",
        action="reactivate",
        current_state=EnrollmentState.CONCLUDED,
    )

    assert result.code == ErrorCodes.INVALID_STATE_TRANSITION
    assert result.message == err.message
    assert result.details is not None
    assert result.details["aggregate_id"] == "enr-1"
    assert result.details["action"] == "reactivate"
    assert result.details["current_state"] == EnrollmentState.CONCLUDED.value
    assert result.details["domain_code"] == "invalid_state_transition"


def test_maps_generic_domain_error_to_state_integrity_violation() -> None:
    err = DomainError(
        code="unexpected_domain_issue",
        message="Unexpected domain issue.",
        details={"foo": "bar"},
    )

    result = to_application_error(
        err=err,
        aggregate_id="enr-1",
        action="conclude",
        current_state=EnrollmentState.ACTIVE,
    )

    assert result.code == ErrorCodes.STATE_INTEGRITY_VIOLATION
    assert result.message == err.message
    assert result.details is not None
    assert result.details["aggregate_id"] == "enr-1"
    assert result.details["action"] == "conclude"
    assert result.details["current_state"] == EnrollmentState.ACTIVE.value
    assert result.details["domain_code"] == "unexpected_domain_issue"
    assert result.details["domain_error"] == "DomainError"
    assert result.details["foo"] == "bar"
