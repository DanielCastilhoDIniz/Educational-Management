from datetime import datetime, timezone

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import EnrollmentCancelled
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


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


def test_pull_without_events() -> None:
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    state_before = enrollment.state
    transitions_before = len(enrollment.transitions)
    events_before = len(enrollment._domain_events)
    # suspended_at_before = enrollment.suspended_at

    events = enrollment.pull_domain_events()
    cancelled_at_before = enrollment.cancelled_at
    concluded_at_before = enrollment.concluded_at

    assert enrollment.state == state_before
    assert enrollment.cancelled_at == cancelled_at_before
    assert enrollment.concluded_at == concluded_at_before
    # assert enrollment.suspended_at == suspended_at_before
    assert len(enrollment.transitions) == transitions_before
    assert len(enrollment._domain_events) == events_before
    assert events == []


def test_pull_cancelled_event() -> None:
    # Arrange
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    justification = "motivo válido"

    enrollment.cancel(actor_id=actor_id, justification=justification)

    state_after_cancel = enrollment.state
    cancelled_at_after_cancel = enrollment.cancelled_at
    transitions_after_cancel = len(enrollment.transitions)
    transitions_copy = list(enrollment.transitions)
    events_count_in_buffer_before_pull = len(enrollment._domain_events)

    # Act
    pulled = enrollment.pull_domain_events()
    pulled2 = enrollment.pull_domain_events()

    # Assert
    assert len(pulled) == 1
    assert len(pulled2) == 0
    assert isinstance(pulled[0], EnrollmentCancelled)
    assert enrollment.state == state_after_cancel
    assert enrollment.cancelled_at == cancelled_at_after_cancel
    assert events_count_in_buffer_before_pull == 1
    assert len(enrollment.transitions) == transitions_after_cancel
    assert enrollment.transitions == transitions_copy
    assert len(enrollment._domain_events) == 0
    assert pulled[0].aggregate_id == enrollment.id
    assert pulled[0].from_state == EnrollmentState.ACTIVE
    assert pulled[0].to_state == EnrollmentState.CANCELLED
    assert pulled[0].actor_id == actor_id
    assert pulled[0].justification == justification
    assert pulled[0].occurred_at is not None
    assert pulled[0].occurred_at == enrollment.cancelled_at
