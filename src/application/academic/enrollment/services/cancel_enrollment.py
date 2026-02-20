from datetime import datetime

from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from application.academic.enrollment.errors.enrollment_errors import EnrollmentNotFoundError
from application.academic.enrollment.dto.results import ApplicationResult


class CancelEnrollmentService:
    """Application service to cancel an enrollment.
    Responsibilities:
- Orchestrate the process of canceling an enrollment, including:
    - Retrieving the enrollment aggregate.
    - Emitting appropriate domain events (EnrollmentConcluded or EnrollmentCancelled).
    - Persisting the updated aggregate state.    """
    repo: EnrollmentRepository

    def __init__(self, repo: EnrollmentRepository):
        self.repo = repo

    def execute(
            self,
            *,
            enrollment_id: str,
            actor_id: str,
            justification: str,
            occurred_at: datetime | None = None,
    ) -> ApplicationResult:
        enrollment = self.repo.get_by_id(enrollment_id)
        if enrollment is None:
            raise EnrollmentNotFoundError(enrollment_id)

        before_state = enrollment.state

        enrollment.cancel(
            actor_id=actor_id,
            occurred_at=occurred_at,
            justification=justification
        )

        changed = enrollment.state != before_state

        if changed:
            self.repo.save(enrollment)
            events = tuple(enrollment.pull_domain_events())
        else:
            events = ()

        new_state = enrollment.state.value if changed else None

        return ApplicationResult(
            aggregate_id=enrollment.id,
            changed=changed,
            events=events,
            new_state=new_state)
