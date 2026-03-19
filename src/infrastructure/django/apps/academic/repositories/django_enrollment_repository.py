from domain.academic.enrollment.entities.enrollment import Enrollment

from infrastructure.errors.persistence_errors import EnrollmentPersistenceNotFoundError, ConcurrencyConflictError

from apps.academic.mappers.enrollment_mapper import EnrollmentMapper
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel

from django.db import transaction
from django.db import IntegrityError, DatabaseError
from infrastructure.errors.persistence_errors import InfrastructureError


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
            Increments the version
            Persists in the database
            Returns the new version
        """

        origin_id = enrollment.id
        origin_version = enrollment.version

        new_version = origin_version + 1

        state = enrollment.state.value
        concluded_at = enrollment.concluded_at
        cancelled_at = enrollment.cancelled_at
        suspended_at = enrollment.suspended_at
        version = new_version
        try:
            with transaction.atomic():
                lines_updated = EnrollmentModel.objects.filter(id=origin_id, version=origin_version).update(
                    state=state,
                    concluded_at=concluded_at,
                    cancelled_at=cancelled_at,
                    suspended_at=suspended_at,
                    version=version,
                )
                if lines_updated == 0:
                    if EnrollmentModel.objects.filter(id=origin_id).exists():
                        raise ConcurrencyConflictError(
                            code="version_mismatch",
                            message="The record exists, but the current persisted" \
                                    "`version` does not match the source `version` of the aggregate.",
                            details={
                                "aggregate_id": enrollment.id,
                                "expected_version": enrollment.version
                                }
                        )
                    else:
                        raise EnrollmentPersistenceNotFoundError(
                            code="enrollment_not_found",
                            message="The enrollment provided does not exist or has not found",
                            details={"enrollment_id": enrollment.id}
                        )
                else:
                    return new_version
        except IntegrityError as e:
            raise InfrastructureError(
                code="integrity_error",
                message="A constraint violation occurred in the database.",
                details={"error": str(e)}
            )
        except DatabaseError as e:
            raise InfrastructureError(
                code="database_error",
                message="A critical error occurred on the database server.",
                details={"error": str(e)}
            )


