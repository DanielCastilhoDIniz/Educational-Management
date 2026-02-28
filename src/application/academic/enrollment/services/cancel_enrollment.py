from datetime import datetime

from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository

from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes


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
            enrollment.cancel(
                actor_id=actor_id,
                occurred_at=occurred_at,
                justification=justification
            )
        except InvalidStateTransitionError as e:
            return ApplicationResult(
                aggregate_id=enrollment_id,
                success=False,
                changed=False,
                error=ApplicationError(
                    code="invalid_state_transition",
                    message=str(e),
                    details={
                        "enrollment_id": enrollment_id,
                        "current_state": enrollment.state.value,
                        "attempted_action": "cancel"
                    }
                )
            )

        changed = enrollment.state != before_state

        if changed:
            self.repo.save(enrollment)
            domain_events = tuple(enrollment.pull_domain_events())
        else:
            domain_events = ()

        new_state = enrollment.state.value if changed else None

        return ApplicationResult(
            aggregate_id=enrollment.id,
            changed=changed,
            success=True,
            domain_events=domain_events,
            new_state=new_state,
        )
