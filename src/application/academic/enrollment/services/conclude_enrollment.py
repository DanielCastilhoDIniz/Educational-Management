from datetime import datetime

from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes

from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict
from domain.academic.enrollment.errors.enrollment_errors import DomainError


class ConcludeEnrollmentService:
    """Application service to conclude an enrollment.
    Responsibilities:
    - Orchestrate the process of concluding an enrollment, including:
    - Retrieving the enrollment aggregate.
    - Emitting appropriate domain events (EnrollmentConcluded).
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

        """
        Execute the conclude enrollment process.
        Steps:
        - Retrieve the enrollment aggregate.
        """

        enrollment = self.repo.get_by_id(enrollment_id)
        if enrollment is None:
            return ApplicationResult(
                aggregate_id=enrollment_id,
                success=False,
                changed=False,
                domain_events=(),
                new_state=None,
                error=ApplicationError(
                    code=ErrorCodes.ENROLLMENT_NOT_FOUND,
                    message=f"Enrollment with id {enrollment_id} not found.",
                    details={"enrollment_id": enrollment_id}
                )
            )
        try:
            enrollment.conclude(
                actor_id=actor_id,
                verdict=verdict,
                occurred_at=occurred_at,
                justification=justification
            )
        except DomainError:
            return ApplicationResult(
                aggregate_id=enrollment_id,
                success=False,
                changed=False,
                domain_events=(),
                new_state=None,
                error=ApplicationError(
                    code=ErrorCodes.INVALID_STATE_TRANSITION,
                    message=f"Enrollment with id {enrollment_id} cannot be concluded from state {enrollment.state.value}.",
                    details={
                        "enrollment_id": enrollment_id,
                        "current_state": enrollment.state.value
                    }
                )
            )
        domain_events = tuple(enrollment.pull_domain_events())

        changed = bool(domain_events)

        if changed:
            self.repo.save(enrollment)

            new_state = enrollment.state

            return ApplicationResult(
                aggregate_id=enrollment.id,
                changed=changed,
                success=True,
                domain_events=domain_events,
                new_state=new_state,
                error=None,
            )
