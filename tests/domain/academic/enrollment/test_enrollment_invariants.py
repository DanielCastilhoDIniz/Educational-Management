from datetime import UTC, datetime

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.shared.domain_error import DomainError


def make_enrollment(*, state: EnrollmentState = EnrollmentState.ACTIVE) -> Enrollment:
    now = datetime.now(UTC)
    concluded_at = now if state == EnrollmentState.CONCLUDED else None
    suspended_at = now if state == EnrollmentState.SUSPENDED else None
    cancelled_at = now if state == EnrollmentState.CANCELLED else None

    return Enrollment(
        id="enr-1",
        institution_id="inst-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_by="user-1",
        created_at=now,
        concluded_at=concluded_at,
        suspended_at=suspended_at,
        cancelled_at=cancelled_at,
    )


def test_enrollment_normalizes_valid_string_state() -> None:
    now = datetime.now(UTC)

    enrollment = Enrollment(
        id="enr-1",
        institution_id="inst-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=EnrollmentState.ACTIVE,
        created_by="user-1",
        created_at=now,
    )

    assert enrollment.state == EnrollmentState.ACTIVE


def test_enrollment_rejects_invalid_string_state() -> None:
    now = datetime.now(UTC)

    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            institution_id="inst-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state="BROKEN_STATE",
            created_by="user-1",
            created_at=now,
        )

    err = exc_info.value
    assert err.code == "invalid_state"
    assert err.details == {"state": "BROKEN_STATE"}


def test_enrollment_rejects_invalid_state_type() -> None:
    now = datetime.now(UTC)

    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            institution_id="inst-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=123,
            created_by="user-1",
            created_at=now,
        )

    err = exc_info.value
    assert err.code == "invalid_state_type"
    assert err.details == {"type": "int"}


def test_enrollment_rejects_invalid_version() -> None:
    now = datetime.now(UTC)

    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            institution_id="inst-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=EnrollmentState.ACTIVE,
            created_by="user-1",
            created_at=now,
            version=0,
        )

    err = exc_info.value
    assert err.code == "invalid_version"
    assert err.details == {"version": 0}


def test_enrollment_rejects_forbidden_timestamp_for_state() -> None:
    now = datetime.now(UTC)

    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            institution_id="inst-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=EnrollmentState.ACTIVE,
            created_by="user-1",
            created_at=now,
            cancelled_at=now,
        )

    err = exc_info.value
    assert err.code == "inconsistent_timestamps"
    assert err.details == {
        "state": EnrollmentState.ACTIVE.value,
        "forbidden_field": "cancelled_at",
    }


def test_enrollment_rejects_none_created_at() -> None:
    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            institution_id="inst-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=EnrollmentState.ACTIVE,
            created_by="user-1",
            created_at=None,
        )

    err = exc_info.value
    assert err.code == "invalid_datetime"
    assert err.details == {"field": "created_at"}


def test_enrollment_rejects_invalid_created_at_type() -> None:
    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            institution_id="inst-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=EnrollmentState.ACTIVE,
            created_by="user-1",
            created_at="2026-01-01",
        )

    err = exc_info.value
    assert err.code == "invalid_datetime_type"
    assert err.details == {"field": "created_at", "type": "str"}


def test_enrollment_normalizes_naive_created_at_to_utc() -> None:
    naive_created_at = datetime(2026, 1, 1, 12, 0)

    enrollment = Enrollment(
        id="enr-1",
        institution_id="inst-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=EnrollmentState.ACTIVE,
        created_by="user-1",
        created_at=naive_created_at,
    )

    assert enrollment.created_at.tzinfo == UTC
    assert enrollment.created_at.hour == 12
    assert enrollment.created_at.minute == 0


def test_validate_state_integrity_rejects_unknown_state_defensively() -> None:
    enrollment = make_enrollment()
    enrollment.state = "BROKEN_STATE"

    with pytest.raises(DomainError) as exc_info:
        enrollment._validate_state_integrity()

    err = exc_info.value
    assert err.code == "invalid_state"
    assert err.details == {"state": "BROKEN_STATE"}
