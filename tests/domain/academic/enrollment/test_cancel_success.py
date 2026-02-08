# tests/domain/academic/enrollment/test_cancel_success.py

from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import (
    EnrollmentCancelled)
from domain.academic.enrollment.value_objects.enrollment_status import (
    EnrollmentState)
from domain.academic.enrollment.errors.enrollment_errors import (
    JustificationRequiredError,
    InvalidStateTransitionError)


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


def assert_cancel_success(
    enrollment: Enrollment,
    *,
    expected_from: EnrollmentState,
    actor_id: str,
    justification: str,
    expected_occurred_at: datetime | None = None,
) -> None:
    """Asserts comuns para cenários de cancelamento com sucesso."""
    # Estado final
    assert enrollment.state == EnrollmentState.CANCELLED

    # Transição
    assert len(enrollment.transitions) == 1
    t = enrollment.transitions[-1]
    assert t.from_state == expected_from
    assert t.to_state == EnrollmentState.CANCELLED
    assert t.actor_id == actor_id
    assert t.justification == justification
    assert t.occurred_at is not None

    # Evento
    assert len(enrollment._domain_events) == 1
    e = enrollment._domain_events[-1]
    assert isinstance(e, EnrollmentCancelled)
    assert e.aggregate_id == enrollment.id
    assert e.from_state == expected_from
    assert e.to_state == EnrollmentState.CANCELLED
    assert e.actor_id == actor_id
    assert e.justification == justification
    assert e.occurred_at is not None

    assert enrollment.cancelled_at is not None
    assert enrollment.cancelled_at == t.occurred_at
    assert enrollment.cancelled_at == e.occurred_at

    # Consistência forte (pega bug bobo)
    assert e.occurred_at == t.occurred_at

    # Se o teste forneceu occurred_at
    # explícito, ele precisa ser exatamente respeitado
    if expected_occurred_at is not None:
        assert t.occurred_at == expected_occurred_at
        assert e.occurred_at == expected_occurred_at


def test_cancel_from_active_success() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    justification = "motivo válido"

    # Act
    enrollment.cancel(actor_id=actor_id, justification=justification)

    # Assert
    assert_cancel_success(
        enrollment,
        expected_from=EnrollmentState.ACTIVE,
        actor_id=actor_id,
        justification=justification,
    )


def test_cancel_from_suspended_success() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.SUSPENDED)
    actor_id = "u-1"
    justification = "motivo válido"

    # Act
    enrollment.cancel(actor_id=actor_id, justification=justification)

    # Assert
    assert_cancel_success(
        enrollment,
        expected_from=EnrollmentState.SUSPENDED,
        actor_id=actor_id,
        justification=justification,
    )


def test_cancel_with_explicit_occurred_at_success() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    justification = "motivo válido"
    occurred_at = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    # Act
    enrollment.cancel(
        actor_id=actor_id,
        justification=justification,
        occurred_at=occurred_at,
    )

    # Assert
    assert_cancel_success(
        enrollment,
        expected_from=EnrollmentState.ACTIVE,
        actor_id=actor_id,
        justification=justification,
        expected_occurred_at=occurred_at,
    )


def test_cancel_from_concluded_raises_invalid_transition() -> None:
    # Arrange: enrollment concluído (válido)
    enrollment = make_enrollment(state=EnrollmentState.CONCLUDED)

    # Arrange: baseline (provar que nada muda)
    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    cancelled_at_before = enrollment.cancelled_at

    # Act: tentativa de cancelar deve falhar
    with pytest.raises(InvalidStateTransitionError) as exc_info:
        enrollment.cancel(actor_id="u-1", justification="motivo válido")

    # Assert: erro correto + contrato mínimo
    err = exc_info.value
    assert err.details is not None
    assert err.code == "invalid_state_transition"
    assert err.details["attempted_action"] == "cancel"
    assert err.details["current_state"] == EnrollmentState.CONCLUDED.value

    # Assert: não houve efeitos colaterais
    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before
    assert enrollment.cancelled_at == cancelled_at_before


def test_cancel_is_idempotent_when_already_cancelled() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.CANCELLED)
    actor_id = "u-1"
    justification = "motivo válido"

    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    cancelled_att_before = enrollment.cancelled_at

    transitions_copy = list(enrollment.transitions)
    events_copy = list(enrollment._domain_events)
    # Act
    enrollment.cancel(actor_id=actor_id, justification=justification)

    # Assert
    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before
    assert enrollment.cancelled_at == cancelled_att_before

    assert enrollment.transitions == transitions_copy
    assert enrollment._domain_events == events_copy


def test_cancel_when_justification_required_raises_error() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    cancelled_at_before = enrollment.cancelled_at

    # Act + Assert
    with pytest.raises(JustificationRequiredError) as exc_info:
        enrollment.cancel(actor_id=actor_id, justification="")

    err = exc_info.value
    assert err.code == "required_justification"
    assert err.message == "justification is required to cancel enrollment"
    assert err.details is not None
    assert err.details["policy"] == "justification_required"

    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before  # <-
    assert enrollment.cancelled_at == cancelled_at_before


