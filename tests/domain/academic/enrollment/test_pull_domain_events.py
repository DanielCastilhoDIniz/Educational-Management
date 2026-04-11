from datetime import UTC, datetime

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.events.enrollment_events import EnrollmentCancelled
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def make_enrollment(*, state: EnrollmentState) -> Enrollment:
    """Factory mínima para criar um Enrollment válido
      para testes de domínio."""
    now = datetime.now(UTC)
    cancelled_at = now if state == EnrollmentState.CANCELLED else None
    concluded_at = now if state == EnrollmentState.CONCLUDED else None
    suspended_at = now if state == EnrollmentState.SUSPENDED else None

    return Enrollment(
        id="enr-1",
        institution_id="inst-1",
        student_id="stu-1",
        class_group_id="cls-1",
        academic_period_id="per-1",
        state=state,
        created_by="user-1",
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


def test_peek_without_events() -> None:
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)

    events = enrollment.peek_domain_events()

    assert events == []
    assert len(enrollment._domain_events) == 0


def test_peek_returns_pending_events_without_clearing_buffer() -> None:
    enrollment = make_enrollment(state=EnrollmentState.ACTIVE)
    actor_id = "u-1"
    justification = "motivo válido"

    enrollment.cancel(actor_id=actor_id, justification=justification)

    first_peek = enrollment.peek_domain_events()
    second_peek = enrollment.peek_domain_events()

    assert len(first_peek) == 1
    assert len(second_peek) == 1
    assert isinstance(first_peek[0], EnrollmentCancelled)
    assert isinstance(second_peek[0], EnrollmentCancelled)
    assert len(enrollment._domain_events) == 1
    assert first_peek[0] is enrollment._domain_events[0]
    assert second_peek[0] is enrollment._domain_events[0]


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
    event = pulled[0]
    assert isinstance(event, EnrollmentCancelled)
    assert enrollment.state == state_after_cancel
    assert enrollment.cancelled_at == cancelled_at_after_cancel
    assert events_count_in_buffer_before_pull == 1
    assert len(enrollment.transitions) == transitions_after_cancel
    assert enrollment.transitions == transitions_copy
    assert len(enrollment._domain_events) == 0
    assert event.aggregate_id == enrollment.id
    assert event.from_state == EnrollmentState.ACTIVE
    assert event.to_state == EnrollmentState.CANCELLED
    assert event.actor_id == actor_id
    assert event.justification == justification
    assert event.occurred_at is not None
    assert event.occurred_at == enrollment.cancelled_at
