import pytest
from datetime import datetime, timezone

from application.academic.enrollment.dto.results import ApplicationResult
from domain.academic.enrollment.events.enrollment_events import EnrollmentConcluded
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


def test_application_result_raises_when_changed_false_and_events_not_empty():
    event = EnrollmentConcluded(
        aggregate_id="enr-1",
        actor_id="user-1",
        occurred_at=datetime.now(timezone.utc),
        from_state=EnrollmentState.ACTIVE,
        to_state=EnrollmentState.CONCLUDED,
    )

    with pytest.raises(ValueError, match="events.*must be empty"):
        ApplicationResult(
            aggregate_id="enr-1",
            changed=False,
            events=[event],
            new_state=None,
        )


def test_application_result_allows_changed_false_with_empty_events():
    result = ApplicationResult(
        aggregate_id="enr-1",
        changed=False,
        events=[],
        new_state=None,
    )

    assert result.changed is False
    assert result.events == []
