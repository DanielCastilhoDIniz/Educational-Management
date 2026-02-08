from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import (
    EnrollmentSuspended)
from domain.academic.enrollment.value_objects.enrollment_status import (
    EnrollmentState)
from domain.academic.enrollment.errors.enrollment_errors import (
    JustificationRequiredError,
    InvalidStateTransitionError,
    DomainError
)


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
    now = datetime.now(timezone.utc)
    cancelled_at = now if state == EnrollmentState.CANCELLED else None
    concluded_at = now if state == EnrollmentState.CONCLUDED else None
    suspended_at = now if state == EnrollmentState.SUSPENDED else None

    return Enrollment(
        id="enr-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        cancelled_at=cancelled_at,
        concluded_at=concluded_at,
        suspended_at=suspended_at,
    )


def assert_suspend_success(
    enrollment: Enrollment,
    *,
    expected_from: EnrollmentState,
    actor_id: str,
    justification: str,
    expected_occurred_at: datetime | None = None,
) -> None:
    """Asserts comuns para cenários de suspenção/trancamento com sucesso."""
    # Estado final
    assert enrollment.state == EnrollmentState.SUSPENDED

    # Transição
    assert len(enrollment.transitions) == 1
    t = enrollment.transitions[-1]
    assert t.from_state == expected_from
    assert t.to_state == EnrollmentState.SUSPENDED
    assert t.actor_id == actor_id
    assert t.justification == justification
    assert t.occurred_at is not None

    # Evento
    assert len(enrollment._domain_events) == 1
    e = enrollment._domain_events[-1]
    assert isinstance(e, EnrollmentSuspended)
    assert e.aggregate_id == enrollment.id
    assert e.from_state == expected_from
    assert e.to_state == EnrollmentState.SUSPENDED
    assert e.actor_id == actor_id
    assert e.justification == justification
    assert e.occurred_at is not None

    assert enrollment.suspended_at is not None
    assert enrollment.suspended_at == t.occurred_at
    assert enrollment.suspended_at == e.occurred_at

    # Consistência forte
    assert e.occurred_at == t.occurred_at

    if expected_occurred_at is not None:
        assert t.occurred_at == expected_occurred_at
        assert e.occurred_at == expected_occurred_at
        assert enrollment.suspended_at == expected_occurred_at


def test_suspend_from_active_success() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    justification = "motivo válido"

    # Act
    enrollment.suspend(actor_id=actor_id, justification=justification)

    # Assert
    assert_suspend_success(
        enrollment,
        expected_from=EnrollmentState.ACTIVE,
        actor_id=actor_id,
        justification=justification,
        expected_occurred_at=None
    )


def test_suspend_with_explicit_occurred_at_success() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    justification = "motivo válido"
    occurred_at = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    # Act
    enrollment.suspend(
        actor_id=actor_id,
        justification=justification,
        occurred_at=occurred_at,
    )

    # Assert
    assert_suspend_success(
        enrollment,
        expected_from=EnrollmentState.ACTIVE,
        actor_id=actor_id,
        justification=justification,
        expected_occurred_at=occurred_at,
    )


def test_suspend_is_idempotent_when_already_suspended() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.SUSPENDED)
    actor_id = "u-1"
    justification = "motivo válido"

    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    suspended_at_before = enrollment.suspended_at

    transitions_copy = list(enrollment.transitions)
    events_copy = list(enrollment._domain_events)
    # Act
    enrollment.suspend(actor_id=actor_id, justification=justification)

    # Assert
    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before
    assert enrollment.suspended_at == suspended_at_before

    assert enrollment.transitions == transitions_copy
    assert enrollment._domain_events == events_copy


def test_suspend_from_concluded_raises_invalid_transition() -> None:
    # Arrange:
    enrollment = make_enrollment(state=EnrollmentState.CONCLUDED)

    # Arrange: baseline
    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    suspended_at_before = enrollment.suspended_at

    transitions_copy = list(enrollment.transitions)
    events_copy = list(enrollment._domain_events)
    # Act:
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        enrollment.suspend(actor_id="u-1", justification="motivo válido")

    # Assert:
    err = exc_info.value
    assert err.details is not None
    assert err.code == "invalid_state_transition"
    assert err.details["attempted_action"] == "suspend"
    assert err.details["current_state"] == EnrollmentState.CONCLUDED.value
    assert err.details["allowed_from_states"] == ["active"]

    # Assert: não houve efeitos colaterais
    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before
    assert enrollment.suspended_at == suspended_at_before

    assert enrollment.transitions == transitions_copy
    assert enrollment._domain_events == events_copy


def test_suspend_from_cancelled_raises_invalid_transition() -> None:
    # Arrange:
    enrollment = make_enrollment(state=EnrollmentState.CANCELLED)

    # Arrange: baseline
    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    suspended_at_before = enrollment.suspended_at

    transitions_copy = list(enrollment.transitions)
    events_copy = list(enrollment._domain_events)
    # Act:
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        enrollment.suspend(actor_id="u-1", justification="motivo válido")

    # Assert:
    err = exc_info.value
    assert err.details is not None
    assert err.code == "invalid_state_transition"
    assert err.details["attempted_action"] == "suspend"
    assert err.details["current_state"] == EnrollmentState.CANCELLED.value
    assert err.details["allowed_from_states"] == ["active"]

    # Assert: não houve efeitos colaterais
    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before
    assert enrollment.suspended_at == suspended_at_before

    assert enrollment.transitions == transitions_copy
    assert enrollment._domain_events == events_copy


def test_suspend_when_justification_required_raises_error() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    suspended_at_before = enrollment.suspended_at

    # Act + Assert
    with pytest.raises(JustificationRequiredError) as exc_info:
        enrollment.suspend(actor_id=actor_id, justification="")

    err = exc_info.value
    assert err.code == "required_justification"
    assert err.message == "justification is required to suspend enrollment"
    assert err.details is not None
    assert err.details["policy"] == "justification_required"

    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before  # <-
    assert enrollment.suspended_at == suspended_at_before


def test_enrollment_suspended_requires_suspended_at() -> None:
    """
    Tests enrollment suspended requires concluded_at
    """
    # Arrange
    now = datetime.now(timezone.utc)

    # Act + Assert
    with pytest.raises(DomainError) as exc_info:
        Enrollment(
            id="enr-1",
            student_id="stu-1",
            class_group_id="cls-1",
            academic_period_id="per-1",
            state=EnrollmentState.SUSPENDED,
            created_at=now,
            suspended_at=None,  # <-
        )

    err = exc_info.value
    assert err.code == "missing_suspended_at"
    assert "Suspended enrollment must have a suspension date" in err.message
