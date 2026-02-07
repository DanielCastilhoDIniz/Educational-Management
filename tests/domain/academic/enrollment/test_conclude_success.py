from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
import domain.academic.enrollment.events.enrollment_events
import domain.academic.enrollment.value_objects.enrollment_status
import domain.academic.enrollment.value_objects.conclusion_verdict
from domain.academic.enrollment.errors.enrollment_errors import (
    InvalidStateTransitionError,
    EnrollmentNotActiveError,
    ConclusionNotAllowedError,
    JustificationRequiredError,
    DomainError
)


def make_enrollment(*, state: domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
    now = datetime.now(timezone.utc)

    concluded_at = now if state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED else None

    return Enrollment(
        id="enr-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        concluded_at=concluded_at,
    )


def assert_conclude_success(
        enrollment: Enrollment,
        *,
        expected_from: domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState,
        actor_id: str,
        expected_occurred_at: datetime,
        justification: str | None = None
        ):
    """Asserts comuns para cenários de conclusão com sucesso"""

    assert enrollment.state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED

    assert enrollment.concluded_at is not None
    assert enrollment.concluded_at == expected_occurred_at

    # transitions
    assert len(enrollment.transitions) == 1
    t = enrollment.transitions[-1]
    assert t.from_state == expected_from
    assert t.to_state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED
    assert t.actor_id == actor_id
    assert t.justification == justification
    assert t.occurred_at == expected_occurred_at

    # events
    assert len(enrollment._domain_events) == 1
    e = enrollment._domain_events[-1]
    assert isinstance(e, domain.academic.enrollment.events.enrollment_events.EnrollmentConcluded)
    assert e.aggregate_id == enrollment.id
    assert e.from_state == expected_from
    assert e.to_state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED
    assert e.actor_id == actor_id
    assert e.justification == justification
    assert e.occurred_at is not None
    assert e.occurred_at == expected_occurred_at

    assert e.occurred_at == t.occurred_at


def test_conclude_from_active_success() -> None:

    # Arrange
    enrollment = make_enrollment(state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE)
    actor_id = "u-1"
    occurred_at = datetime.now(timezone.utc)
    justification = None
    verdict = domain.academic.enrollment.value_objects.conclusion_verdict.ConclusionVerdict()

    # Act
    enrollment.conclude(
        actor_id=actor_id,
        occurred_at=occurred_at,
        justification=justification,
        verdict=verdict
    )

    assert_conclude_success(
        enrollment=enrollment,
        expected_from=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE,
        actor_id=actor_id,
        expected_occurred_at=occurred_at,
        justification=justification
    )


def test_conclude_is_idempotent_when_already_concluded() -> None:

    enrollment = make_enrollment(state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED)
    actor_id = "u-1"
    occurred_at = datetime(2026, 1, 2, 10, 0, tzinfo=timezone.utc)
    verdict = domain.academic.enrollment.value_objects.conclusion_verdict.ConclusionVerdict()

    state_before = enrollment.state
    concluded_before = enrollment.concluded_at
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)

    enrollment.conclude(
        actor_id=actor_id,
        occurred_at=occurred_at,
        justification=None,
        verdict=verdict
    )

    transitions_copy = list(enrollment.transitions)
    events_copy = list(enrollment._domain_events)

    assert enrollment.state == state_before
    assert enrollment.concluded_at is concluded_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before

    assert enrollment.transitions == transitions_copy
    assert enrollment._domain_events == events_copy


def test_conclude_from_not_active_raises_error() -> None:
    enrollment = make_enrollment(state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.SUSPENDED)
    actor_id = "u-1"
    occurred_at = datetime.now(timezone.utc)
    justification = None
    verdict = domain.academic.enrollment.value_objects.conclusion_verdict.ConclusionVerdict()

    with pytest.raises(EnrollmentNotActiveError) as exc_info:
        enrollment.conclude(
            actor_id=actor_id,
            occurred_at=occurred_at,
            justification=justification,
            verdict=verdict
        )
    err = exc_info.value
    assert err.code == "enrollment_not_active"
    assert err.details is not None
    assert err.details["current_state"] == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.SUSPENDED.value
    assert err.details["required_state"] == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE.value
    assert err.details["attempted_action"] == "conclude"


def test_enrollment_requires_valid_id() -> None:
    # Arrange
    now = datetime.now(timezone.utc)

    # Act + Assert
    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="",  # inválido
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE,
            created_at=now,
            concluded_at=None,
        )

    err = exc_info.value
    assert err.code == "invalid_id"


def test_enrollment_concluded_requires_concluded_at() -> None:
    # Arrange
    now = datetime.now(timezone.utc)

    # Act + Assert
    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED,
            created_at=now,
            concluded_at=None,  # <-
        )

    err = exc_info.value
    assert err.code == "missing_concluded_at"
    assert "Concluded enrollment must have a conclusion date" in err.message


def test_enrollment_concluded_fills_occurred_at_automatically() -> None:
    # Arrange
    # Arrange
    enrollment = make_enrollment(state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE)
    actor_id = "u-1"
    justification = None
    verdict = domain.academic.enrollment.value_objects.conclusion_verdict.ConclusionVerdict()

    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    # state_before = enrollment.state
    # concluded_at_before = enrollment.concluded_at

    # Act
    enrollment.conclude(
        actor_id=actor_id,
        justification=justification,
        verdict=verdict
    )

    # Assert
    assert enrollment.state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED
    assert enrollment.concluded_at is not None

    assert len(enrollment.transitions) == transitions_before + 1
    t = enrollment.transitions[-1]
    assert t.occurred_at is not None
    assert t.occurred_at == enrollment.concluded_at
    assert t.from_state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE
    assert t.to_state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED
    assert t.actor_id == actor_id
    assert t.justification == justification

    assert len(enrollment._domain_events) == events_before + 1
    e = enrollment._domain_events[-1]
    assert isinstance(e, domain.academic.enrollment.events.enrollment_events.EnrollmentConcluded)
    assert e.aggregate_id == enrollment.id
    assert e.from_state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE
    assert e.to_state == domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.CONCLUDED
    assert e.actor_id == actor_id
    assert e.justification == justification
    assert e.occurred_at is not None

    assert e.occurred_at == t.occurred_at


def test_should_not_conclude_enrollment_when_verdict_is_disallowed() -> None:
    """
    tests when verdict is not allowed
    """

    enrollment = make_enrollment(state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE)
    actor_id = "u-1"
    # occurred_at = datetime.now(timezone.utc)
    justification = None
    verdict = domain.academic.enrollment.value_objects.conclusion_verdict.ConclusionVerdict(is_allowed=False, reasons=["low frequency"])

    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    concluded_at_before = enrollment.concluded_at

    with pytest.raises(ConclusionNotAllowedError) as exc_info:
        enrollment.conclude(
            actor_id=actor_id,
            justification=justification,
            verdict=verdict,
        )

    assert enrollment.state == state_before
    assert enrollment.concluded_at == concluded_at_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before

    err = exc_info.value
    assert err.code == "enrollment_conclusion_not_allowed"
    assert err.message == "Conclusion is not allowed by policy"  # remove later
    assert err.details is not None  # <---
    assert err.details["reasons"] == verdict.reasons
    assert err.details["attempted_action"] == "conclude"


def test_conclude_when_verdict_raises_justification_required() -> None:
    """
    tests when verdict requires justification
    """
    enrollment = make_enrollment(state=domain.academic.enrollment.value_objects.enrollment_status.EnrollmentState.ACTIVE)
    actor_id = "u-1"
    verdict = domain.academic.enrollment.value_objects.conclusion_verdict.ConclusionVerdict(requires_justification=True)

    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    concluded_at_before = enrollment.concluded_at

    with pytest.raises(JustificationRequiredError) as exc_info:
        enrollment.conclude(
            actor_id=actor_id,
            justification="  ",
            verdict=verdict,
        )
    assert enrollment.state == state_before
    assert enrollment.concluded_at == concluded_at_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before

    err = exc_info.value
    assert err.code == "justification_required"
    assert err.message == "Justification is required to conclude enrollment"
    assert err.details is not None
    assert err.details["policy"] == "requires_justification"
