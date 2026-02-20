from datetime import datetime

from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from application.academic.enrollment.errors.enrollment_errors import EnrollmentNotFoundError
from application.academic.enrollment.dto.results import ApplicationResult

from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict


class ConcludeEnrollmentService:
    """Application service to conclude an enrollment.
    Responsibilities:
- Orchestrate the process of concluding an enrollment, including:
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
            verdict: ConclusionVerdict,
            occurred_at: datetime | None = None,
            justification: str | None = None
            ) -> ApplicationResult:

        """        Conclude an enrollment by applying business rules and emitting domain events.
        Steps:
        1. Retrieve the Enrollment aggregate by id.
        2. Validate existence
        3.Delegate business validation to the domain
        4. Apply the conclusion logic (attendance, grades, period closure, etc.).
        5. Emit an EnrollmentConcluded event if successful, or EnrollmentCancelled if not.
        6. Persist the updated aggregate state.
        7. Return an ApplicationResult with the outcome and emitted events.
        """

        enrollment = self.repo.get_by_id(enrollment_id)
        if enrollment is None:
            raise EnrollmentNotFoundError(enrollment_id)

        before_state = enrollment.state

        enrollment.conclude(
            actor_id=actor_id,
            verdict=verdict,
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
