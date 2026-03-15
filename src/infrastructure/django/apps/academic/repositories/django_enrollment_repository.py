from domain.academic.enrollment.entities.enrollment import Enrollment

from infrastructure.errors.persistence_errors import EnrollmentPersistenceNotFoundError, ConcurrencyConflictError

from apps.academic.mappers.enrollment_mapper import EnrollmentMapper
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel


class DjangoEnrollmentRepository:
    """
        Search for an enrollment_id and persist it in the database
    """

    def get_by_id(self, enrollment_id: str) -> Enrollment | None:
        """
            busca snapshot da matrícula
            carrega transições relacionadas
            reconstrói aggregate
            retorna None só se snapshot não existir
        """
        snapshot = EnrollmentModel.objects.filter(id=enrollment_id).first()

        if snapshot is None:
            return None

        transitions_list = list(
            EnrollmentTransitionModel.objects.filter(enrollment=snapshot).order_by("occurred_at")
        )

        return EnrollmentMapper.to_domain(snapshot=snapshot, transitions=transitions_list)

    def save(self, enrollment: Enrollment) -> int:
        """
            Searches for the snapshot in the database by enrollment_id
            If not found — raises EnrollmentPersistenceNotFoundError
            Checks if the snapshot version matches the aggregate version
            If they don't match — raises ConcurrencyConflictError
            Calls apply_to_snapshot to update the snapshot with the aggregate state
            Increments the version
            Persists in the database
            Returns the new version
        """

        snapshot = EnrollmentModel.objects.filter(id=enrollment.id).first()

        if snapshot is None:
            raise EnrollmentPersistenceNotFoundError(
                code="enrollment_not_found",
                message="The enrollment provided does not exist or has not found",
                details={"enrollment_id": enrollment.id}
            )

        if enrollment.version != snapshot.version:
            raise ConcurrencyConflictError(
                code="version_mismatch",
                message="The record exists, but the current persisted \
                    `version` does not match the source `version` of the aggregate.",
                details={
                    "aggregate_id": enrollment.id,
                    "occurred_at": enrollment.created_at,
                    "current_version": snapshot.version,
                    "expected_version": enrollment.version
                    }
            )
        
        EnrollmentMapper.apply_to_snapshot(enrollment=enrollment, snapshot=snapshot)
        snapshot.version += 1
        snapshot.save()
        enrollment.version += 1

        return enrollment.version
