# tests/domain/academic/enrollment/test_cancel_success.py

from datetime import datetime, timezone

import pytest

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import EnrollmentCancelled
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.academic.enrollment.errors.enrollment_errors import InvalidStateTransitionError


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
    now = datetime.now(timezone.utc)
    concluded_at = now if state == EnrollmentState.CONCLUDED else None

    return Enrollment(
        id="enr-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_at=now,
        concluded_at=concluded_at,
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

    # Act: tentativa de cancelar deve falhar
    with pytest.raises(InvalidStateTransitionError) as excinfo:
        enrollment.cancel(actor_id="u-1", justification="motivo válido")

    # Assert: erro correto + contrato mínimo
    err = excinfo.value
    assert err.code == "invalid_state_transition"
    assert err.details["attempted_action"] == "cancel"
    assert err.details["current_state"] == EnrollmentState.CONCLUDED.value

    # Assert: não houve efeitos colaterais
    assert enrollment.state == state_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before



