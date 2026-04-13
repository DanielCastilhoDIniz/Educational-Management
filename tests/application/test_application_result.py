from datetime import UTC, datetime

import pytest

from application.shared.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.dto.results import ApplicationResult
from domain.academic.enrollment.events.enrollment_events import EnrollmentConcluded
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def test_application_result_raises_when_changed_false_and_events_not_empty():
    event = EnrollmentConcluded(
        aggregate_id="enr-1",
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
        from_state=EnrollmentState.ACTIVE,
        to_state=EnrollmentState.CONCLUDED,
    )

    with pytest.raises(ValueError, match="events.*must be empty"):
        ApplicationResult(
            aggregate_id="enr-1",
            success=True,
            changed=False,
            domain_events=(event,),
            new_state=None,
            error=None,
        )


def test_application_result_allows_changed_false_with_empty_events():
    result = ApplicationResult(
        aggregate_id="enr-1",
        success=True,
        changed=False,
        domain_events=(),
        new_state=None,
        error=None,
    )

    assert result.success is True
    assert result.changed is False
    assert result.domain_events == ()


def test_no_change_success_cannot_include_new_state():
    with pytest.raises(ValueError, match="If 'changed' is False, 'new_state' must be None."):
        ApplicationResult(
            aggregate_id="enr-1",
            success=True,
            changed=False,
            domain_events=(),
            new_state=EnrollmentState.CANCELLED,
            error=None,
        )


def test_changed_success_requires_new_state():
    event = EnrollmentConcluded(
        aggregate_id="enr-1",
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
        from_state=EnrollmentState.ACTIVE,
        to_state=EnrollmentState.CONCLUDED,
    )

    with pytest.raises(ValueError, match="If 'changed' is True, 'new_state' is required."):
        ApplicationResult(
            aggregate_id="enr-1",
            success=True,
            changed=True,
            domain_events=(event,),
            new_state=None,
            error=None,

        )


def test_changed_success_requires_domain_events():
    with pytest.raises(ValueError, match="If 'changed' is True, 'domain_events' must not be empty."):

        ApplicationResult(
            aggregate_id="enr-1",
            success=True,
            changed=True,
            domain_events=(),
            new_state=EnrollmentState.CANCELLED,
            error=None,
        )


def test_success_cannot_include_error():
    event = EnrollmentConcluded(
        aggregate_id="enr-1",
        actor_id="user-1",
        occurred_at=datetime.now(UTC),
        from_state=EnrollmentState.ACTIVE,
        to_state=EnrollmentState.CONCLUDED,
    )

    with pytest.raises(ValueError, match=r"If 'success' is True, 'error' must be None."):

        ApplicationResult(
            aggregate_id="enr-1",
            success=True,
            changed=True,
            domain_events=(event,),
            new_state=EnrollmentState.CONCLUDED,
            error=ApplicationError(
                code=ErrorCodes.ENROLLMENT_NOT_FOUND,
                message="enrollment not found",
                details={
                    "aggregate_id": "enr-1",
                },
            )
        )


def test_failure_cannot_include_change():
    with pytest.raises(ValueError, match=r"If 'success' is False, 'changed' must be False."):

        ApplicationResult(
            aggregate_id="enr-1",
            success=False,
            changed=True,
            domain_events=(),
            new_state=None,
            error=ApplicationError(
                code=ErrorCodes.ENROLLMENT_NOT_FOUND,
                message="enrollment not found",
                details={
                    "aggregate_id": "enr-1",
                },
            )
        )


def test_failure_requires_error():
    with pytest.raises(ValueError, match=r"If 'success' is False, 'error' is required."):
        ApplicationResult(
            aggregate_id="enr-1",
            success=False,
            changed=False,
            domain_events=(),
            new_state=None,
            error=None,
        )


def test_failure_cannot_include_new_state():
    with pytest.raises(ValueError, match=r"If 'success' is False, 'new_state' must be None."):
        ApplicationResult(
            aggregate_id="enr-1",
            success=False,
            changed=False,
            domain_events=(),
            new_state=EnrollmentState.CANCELLED,
            error=ApplicationError(
                code=ErrorCodes.STATE_INTEGRITY_VIOLATION,
                message="state integrity violation",
                details={
                    "aggregate_id": "enr-1",},
            )
        )


def test_failure_cannot_include_domain_events():
    event = EnrollmentConcluded(
            aggregate_id="enr-1",
            actor_id="user-1",
            occurred_at=datetime.now(UTC),
            from_state=EnrollmentState.ACTIVE,
            to_state=EnrollmentState.CONCLUDED,
        )

    with pytest.raises(ValueError, match=r"If 'success' is False, 'domain_events' must be empty."):

        ApplicationResult(
            aggregate_id="enr-1",
            success=False,
            changed=False,
            domain_events=(event,),
            new_state=None,
            error=ApplicationError(
                code=ErrorCodes.STATE_INTEGRITY_VIOLATION,
                message="state integrity violation.",
                details={
                    "aggregate_id": "enr-1",
                
                },
            ),
        )
