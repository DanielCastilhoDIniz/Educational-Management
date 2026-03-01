from datetime import datetime

from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.dto.errors.application_error import ApplicationError
from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.errors.domain_error_mapper import to_application_error

from domain.academic.enrollment.value_objects.conclusion_verdict import ConclusionVerdict
from domain.academic.enrollment.errors.enrollment_errors import DomainError
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


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

    @staticmethod
    def _build_not_found_result(enrollment_id: str) -> ApplicationResult:
        return ApplicationResult(
            aggregate_id=enrollment_id,
            success=False,
            changed=False,
            domain_events=(),
            new_state=None,
            error=ApplicationError(
                code=ErrorCodes.ENROLLMENT_NOT_FOUND,
                message=f"Enrollment with id {enrollment_id} not found.",
                details={
                    "aggregate_id": enrollment_id,
                    "action": "conclude",
                    "current_state": None
                }
            )
        )

    @staticmethod
    def _build_persistence_failure_result(
            *,
            enrollment_id: str,
            current_state: str,
            err: Exception,
    ) -> ApplicationResult:
        return ApplicationResult(
            aggregate_id=enrollment_id,
            success=False,
            changed=False,
            domain_events=(),
            new_state=None,
            error=ApplicationError(
                code=ErrorCodes.UNEXPECTED_ERROR,
                message="Failed to persist enrollment conclusion.",
                details={
                    "aggregate_id": enrollment_id,
                    "action": "conclude",
                    "current_state": current_state,
                    "exception_type": err.__class__.__name__,
                    "exception_message": str(err),
                }
            )
        )

    @staticmethod
    def _build_domain_failure_result(
            *,
            enrollment_id: str,
            current_state: EnrollmentState,
            action: str,
            err: DomainError,
    ) -> ApplicationResult:
        return ApplicationResult(
            aggregate_id=enrollment_id,
            success=False,
            changed=False,
            domain_events=(),
            new_state=None,
            error=to_application_error(
                err=err,
                aggregate_id=enrollment_id,
                action=action,
                current_state=current_state
            )
        )

    @staticmethod
    def _build_state_integrity_result(
            *,
            enrollment_id: str,
            previous_state: str,
            current_state: str,
            reason: str,
            message: str,
    ) -> ApplicationResult:
        return ApplicationResult(
            aggregate_id=enrollment_id,
            success=False,
            changed=False,
            domain_events=(),
            new_state=None,
            error=ApplicationError(
                code=ErrorCodes.STATE_INTEGRITY_VIOLATION,
                message=message,
                details={
                    "aggregate_id": enrollment_id,
                    "action": "conclude",
                    "previous_state": previous_state,
                    "current_state": current_state,
                    "reason": reason,
                }
            )
        )

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
            return self._build_not_found_result(enrollment_id)
        previous_state = enrollment.state
        try:
            enrollment.conclude(
                actor_id=actor_id,
                verdict=verdict,
                occurred_at=occurred_at,
                justification=justification
            )
        except DomainError as err:
            return self._build_domain_failure_result(
                enrollment_id=enrollment_id,
                current_state=enrollment.state,
                action="conclude",
                err=err,
            )
        state_changed = enrollment.state != previous_state
        events_snapshot = tuple(enrollment.peek_domain_events())

        if not state_changed:
            if events_snapshot:
                return self._build_state_integrity_result(
                    enrollment_id=enrollment_id,
                    previous_state=previous_state.value,
                    current_state=enrollment.state.value,
                    reason="event_without_state_change",
                    message="Conclusion produced pending domain events without a state change.",
                )
            return ApplicationResult(
                aggregate_id=enrollment_id,
                changed=False,
                success=True,
                domain_events=(),
                new_state=None,
                error=None
            )
        if not events_snapshot:
            return self._build_state_integrity_result(
                enrollment_id=enrollment_id,
                previous_state=previous_state.value,
                current_state=enrollment.state.value,
                reason="state_changed_without_event",
                message="Conclusion changed state without emitting a domain event.",
            )

        try:
            self.repo.save(enrollment)
        except Exception as err:
            return self._build_persistence_failure_result(
                enrollment_id=enrollment_id,
                current_state=enrollment.state.value,
                err=err,
            )

        enrollment.pull_domain_events()

        return ApplicationResult(
            aggregate_id=enrollment_id,
            changed=True,
            success=True,
            domain_events=events_snapshot,
            new_state=enrollment.state,
            error=None
        )
