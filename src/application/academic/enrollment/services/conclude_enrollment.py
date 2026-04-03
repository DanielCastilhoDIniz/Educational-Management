from datetime import datetime

from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from application.academic.enrollment.services._state_change_flow import (
    build_domain_failure_result,
    build_not_found_result,
    finalize_state_change,
)
from domain.academic.enrollment.errors.enrollment_errors import DomainError
from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict


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
            return build_not_found_result(enrollment_id=enrollment_id, action="conclude")
        previous_state = enrollment.state
        try:
            enrollment.conclude(
                actor_id=actor_id,
                verdict=verdict,
                occurred_at=occurred_at,
                justification=justification
            )
        except DomainError as err:
            return build_domain_failure_result(
                enrollment_id=enrollment_id,
                current_state=enrollment.state,
                action="conclude",
                err=err,
            )
        return finalize_state_change(
            repo=self.repo,
            enrollment=enrollment,
            enrollment_id=enrollment_id,
            action="conclude",
            previous_state=previous_state,
            persistence_failure_message="Failed to persist enrollment conclusion.",
            event_without_state_change_message="Conclusion produced pending domain events without a state change.",
            state_changed_without_event_message="Conclusion changed state without emitting a domain event.",
        )
