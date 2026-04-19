from datetime import datetime
from typing import cast

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.dto.results import ApplicationResult
from application.academic.enrollment.errors.persistence_errors import (
    EnrollmentDuplicationError,
    EnrollmentTechnicalPersistenceError,
)
from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from application.academic.enrollment.services._state_change_flow import (
    build_persistence_failure_result,
)
from domain.academic.enrollment.entities.enrollment import Enrollment


class CreateEnrollment:
    """Application service to create an enrollment.
    Responsibilities:
    - Orchestrate the process of creating an enrollment, including:
    - Retrieving the enrollment aggregate.
    - Emitting appropriate domain events (EnrollmentCreated).
    - Persisting the updated aggregate state.
    """
    repo: EnrollmentRepository

    def __init__(self, repo: EnrollmentRepository):
        self.repo = repo

    def execute(
            self,
            *,
            institution_id: str,
            student_id: str,
            class_group_id: str,
            academic_period_id: str,
            actor_id: str,
            occurred_at: datetime | None = None
            ) -> ApplicationResult:
        """
        Execute the create enrollment process.
        Steps:
        - Create a new enrollment aggregate.
        - Persist the new aggregate state.
        """

        enrollment = Enrollment.create(
            institution_id=institution_id,
            student_id=student_id,
            class_group_id=class_group_id,
            academic_period_id=academic_period_id,
            actor_id=actor_id,
            occurred_at=occurred_at
        )

        try:
            self.repo.create(enrollment)
        except EnrollmentDuplicationError as e:
            return build_persistence_failure_result(
                enrollment_id=enrollment.id,
                action="create",
                current_state=enrollment.state,
                code=ErrorCodes.DUPLICATE_ENROLLMENT,
                message="An enrollment with the same identifiers already exists.",
                err=e,
            )

        except EnrollmentTechnicalPersistenceError as e:
            return build_persistence_failure_result(
                enrollment_id=enrollment.id,
                action="create",
                current_state=enrollment.state,
                code=cast(ErrorCodes, e.code),
                message="Failed to create enrollment due to a technical persistence error.",
                err=e,
            )
        
        return ApplicationResult(
            aggregate_id=enrollment.id,
            changed=True,
            success=True,
            domain_events=tuple(enrollment.pull_domain_events()),
            new_state=enrollment.state,
            error=None
        )