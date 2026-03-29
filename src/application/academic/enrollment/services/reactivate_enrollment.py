from datetime import datetime

from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from application.academic.enrollment.services._state_change_flow import (
    build_domain_failure_result,
    build_not_found_result,
    finalize_state_change,
)
from domain.academic.enrollment.errors.enrollment_errors import DomainError


class ReactivateEnrollmentService:    
    """Application service to reactivate an enrollment.
    Responsibilities:
    - Orchestrate the process of reactivating an enrollment, including:
    - Retrieving the enrollment aggregate.
    - Emitting appropriate domain events (EnrollmentReactivated).
    - Persisting the updated aggregate state.
    """
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
        """
        Execute the reactivate enrollment process.
        Steps:
        - Retrieve the enrollment aggregate.
        """
        enrollment = self.repo.get_by_id(enrollment_id)
        if enrollment is None:
            return build_not_found_result(enrollment_id=enrollment_id, action="reactivate")
        
        previous_state = enrollment.state
        try:
            enrollment.reactivate(
                actor_id=actor_id,
                occurred_at=occurred_at,
                justification=justification
            )
        except DomainError as err:
            return build_domain_failure_result(
                enrollment_id=enrollment_id,
                current_state=enrollment.state,
                action="reactivate",
                err=err,
            )
            
        return finalize_state_change(
            repo=self.repo,
            enrollment=enrollment,
            enrollment_id=enrollment_id,
            action="reactivate",
            previous_state=previous_state,
            persistence_failure_message="Failed to persist enrollment reactivation.",
            event_without_state_change_message="Reactivation produced pending domain events without a state change.",
            state_changed_without_event_message="Reactivation changed state without emitting a domain event.",
        )
