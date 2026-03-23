from datetime import UTC, datetime

from django.db import DatabaseError, IntegrityError, transaction

from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from apps.academic.mappers.enrollment_mapper import EnrollmentMapper
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel
from domain.academic.enrollment.entities.enrollment import Enrollment
from infrastructure.errors.persistence_errors import (
    ConcurrencyConflictError,
    EnrollmentPersistenceNotFoundError,
    InfrastructureError,
)


class DjangoEnrollmentRepository(EnrollmentRepository):
    """
        Concrete Django implementation of the EnrollmentRepository port.

        Responsible for:
        - loading an Enrollment aggregate from snapshot + transitions
        - persisting snapshot updates with optimistic concurrency control
        - ensure that persists the latest transition in the same transaction.
    """

    def get_by_id(self, enrollment_id: str) -> Enrollment | None:
        """
        Load the enrollment snapshot and its transitions, then reconstruct
        the aggregate.

        Returns:
            Enrollment | None:
                - None only when the snapshot does not exist
                - Enrollment aggregate otherwise

        Raises:
            Any mapper/persistence inconsistency exception is allowed to propagate.
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
        Persist an existing Enrollment aggregate using optimistic concurrency control.

        Semantics:
        - Uses enrollment.version as the origin version.
        - Updates the snapshot only if (id, version) still matches in persistence.
        - Persists the latest transition in the same transaction.
        - Returns the newly persisted version.

        Args:
            enrollment: Enrollment aggregate to be persisted.

        Returns:
            int: Newly persisted version number.

        Raises:
            EnrollmentPersistenceNotFoundError:
                If the enrollment snapshot does not exist.
            ConcurrencyConflictError:
                If the snapshot exists but the persisted version differs from
                the aggregate origin version.
            InfrastructureError:
                For integrity, database-level technical failures or missing  transitions list.
        """

        origin_id = enrollment.id
        origin_version = enrollment.version

        state = enrollment.state.value
        concluded_at = enrollment.concluded_at
        cancelled_at = enrollment.cancelled_at
        suspended_at = enrollment.suspended_at
        new_version = origin_version + 1
        now = datetime.now(UTC)

        if not enrollment.transitions:
            raise InfrastructureError(
                code="missing_transition",
                message="Cannot persist enrollment because no transition was provided.",
                details={"enrollment_id": origin_id},
            )

        try:
            with transaction.atomic():
                updated_rows = EnrollmentModel.objects.filter(id=origin_id, version=origin_version).update(
                    state=state,
                    concluded_at=concluded_at,
                    cancelled_at=cancelled_at,
                    suspended_at=suspended_at,
                    version=new_version,
                    updated_at=now
                )

                if updated_rows == 0:
                    if EnrollmentModel.objects.filter(id=origin_id).exists():
                        raise ConcurrencyConflictError(
                            code="version_mismatch",
                            message="The enrollment exists, but its persisted version \
                                  does not match the aggregate origin version.",
                            details={
                                "aggregate_id": enrollment.id,
                                "expected_version": enrollment.version
                                }
                        )
                    else:
                        raise EnrollmentPersistenceNotFoundError(
                            code="enrollment_not_found",
                            message="The enrollment snapshot was not found for persistence update.",
                            details={
                                        "enrollment_id": origin_id,
                                        "origin_version": origin_version,
                                        "attempted_new_version": new_version,
                                    }
                        )
                else:

                    EnrollmentMapper.to_transition(
                        state_transition=enrollment.transitions[-1],
                        enrollment_id=origin_id
                    ).save()
                    return new_version
        except(EnrollmentPersistenceNotFoundError, ConcurrencyConflictError):
            raise

        except IntegrityError as e:
            raise InfrastructureError(
                code="integrity_error",
                message="A constraint violation occurred in the database.",
                details={"error": str(e)}
            ) from e
        except DatabaseError as e:
            raise InfrastructureError(
                code="database_error",
                message="A critical error occurred on the database server.",
                details={"error": str(e)}
            ) from e

