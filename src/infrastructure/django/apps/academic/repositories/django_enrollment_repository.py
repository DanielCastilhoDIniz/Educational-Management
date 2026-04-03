from datetime import UTC, datetime

from django.db import DatabaseError, IntegrityError, transaction

from application.academic.enrollment.dto.errors.error_codes import ErrorCodes
from application.academic.enrollment.errors.persistence_errors import (
    ConcurrencyConflictError,
    EnrollmentCreationError,
    EnrollmentPersistenceNotFoundError,
    EnrolmentDuplicationError,
)
from application.academic.enrollment.ports.enrollment_repository import EnrollmentRepository
from apps.academic.mappers.enrollment_mapper import EnrollmentMapper
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel
from domain.academic.enrollment.entities.enrollment import Enrollment
from infrastructure.errors.persistence_errors import (
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

    @staticmethod
    def _is_same_persisted_snapshot(
        *,
        snapshot: EnrollmentModel,
        state: str,
        concluded_at: datetime | None,
        cancelled_at: datetime | None,
        suspended_at: datetime | None,
        reactivated_at: datetime | None,
        version: int,
    ) -> bool:
        return (
            snapshot.state == state
            and snapshot.concluded_at == concluded_at
            and snapshot.cancelled_at == cancelled_at
            and snapshot.suspended_at == suspended_at
            and snapshot.reactivated_at == reactivated_at
            and snapshot.version == version
        )

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
        # Extracting aggregate metadata for persistence logic
        origin_id = enrollment.id
        origin_version = enrollment.version

        state = enrollment.state.value
        concluded_at = enrollment.concluded_at
        cancelled_at = enrollment.cancelled_at
        suspended_at = enrollment.suspended_at
        reactivated_at = enrollment.reactivated_at

        new_version = origin_version + 1
        now = datetime.now(UTC)

        # Ensure there is at least one transition to persist (Audit Trail requirement)
        if not enrollment.transitions:
            raise InfrastructureError(
                code="missing_transition",
                message="Cannot persist enrollment because no transition was provided.",
                details={"enrollment_id": origin_id},
            )

        try:
            # Atomic block to ensure Snapshot and Transition are persisted together
            with transaction.atomic():
                updated_rows = EnrollmentModel.objects.filter(id=origin_id, version=origin_version).update(
                    state=state,
                    concluded_at=concluded_at,
                    cancelled_at=cancelled_at,
                    suspended_at=suspended_at,
                    reactivated_at=reactivated_at,
                    version=new_version,
                    updated_at=now
                )

                # Handle cases where no rows were updated (Conflict or Not Found)
                if updated_rows == 0:
                    persisted_snapshot = EnrollmentModel.objects.filter(id=origin_id).first()

                    if persisted_snapshot is not None:
                        persisted_transition = EnrollmentMapper.to_transition(
                            state_transition=enrollment.transitions[-1],
                            enrollment_id=origin_id,
                        )

                        if (
                            EnrollmentTransitionModel.objects.filter(
                                transition_id=persisted_transition.transition_id
                            ).exists()
                            and self._is_same_persisted_snapshot(
                                snapshot=persisted_snapshot,
                                state=state,
                                concluded_at=concluded_at,
                                cancelled_at=cancelled_at,
                                suspended_at=suspended_at,
                                reactivated_at=reactivated_at,
                                version=new_version,
                            )
                        ):
                            return new_version

                        # Raise conflict error if the version in the DB is different
                        raise ConcurrencyConflictError(
                            code="version_mismatch",
                            message="The enrollment exists, but its persisted version \
                                  does not match the aggregate origin version.",
                            details={
                                "aggregate_id": enrollment.id,
                                "expected_version": enrollment.version,

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
                    
                    # Successful update: Persist the latest transition
                    EnrollmentMapper.to_transition(
                        state_transition=enrollment.transitions[-1],
                        enrollment_id=origin_id
                    ).save()
                    return new_version
        
        # Raise conflict error if the version in the DB is different
        except(EnrollmentPersistenceNotFoundError, ConcurrencyConflictError):
            raise

        except DatabaseError as e:
            raise InfrastructureError(
                code="database_error",
                message="A critical error occurred on the database server.",
                details={"error": str(e)}
            ) from e


    def create(self, enrollment: Enrollment) ->int:

        try:

            with transaction.atomic():
                snapshot = EnrollmentMapper.to_snapshot(enrollment=enrollment)
                snapshot.save()

                return snapshot.version
            
        except IntegrityError as e:
            raise EnrolmentDuplicationError(
                code=ErrorCodes.DUPLICATE_ENROLLMENT,
                message="An enrollment with the same identifiers already exists.",
                details={"enrollment_id": enrollment.id},
            ) from e
        except Exception as e:
            raise EnrollmentCreationError(
                code=ErrorCodes.ENROLLMENT_CREATION_FAILED,
                message="Failed to create enrollment due to a integrity error.",
            ) from e

        
       