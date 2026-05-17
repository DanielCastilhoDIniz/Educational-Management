from datetime import UTC, datetime

from django.db import DatabaseError, IntegrityError, transaction

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.errors.persistence_errors import (
    ConcurrencyConflictError,
    UserDuplicationError,
    UserPersistenceNotFoundError,
    UserTechnicalPersistenceError,
)
from application.identity.user.ports.user_repository import UserRepository
from apps.identity.mappers.user_mapper import UserMapper
from apps.identity.models.user_model import UserModel
from apps.identity.models.user_transition_model import UserTransitionModel
from domain.identity.user.entities.user import User


class DjangoUserRepository(UserRepository):
    """
        Concrete Django implementation of the UserRepository port.

        Responsible for:
        - loading a User aggregate from snapshot + transitions
        - persisting snapshot updates with optimistic concurrency control
        - ensure that persists the latest transition in the same transaction.
    """

    
    def get_by_id(self, user_id: str) -> User | None:
        """
        Load the user snapshot and its transitions, then reconstruct
        the aggregate.

        Returns:
            User | None:
                - None only when the snapshot does not exist
                - User aggregate otherwise

        Raises:
            Any mapper/persistence inconsistency exception is allowed to propagate.
        """

        snapshot = UserModel.objects.filter(id=user_id).first()

        if snapshot is None:
            return None
        
        transitions_list = list(
            UserTransitionModel.objects.filter(user=snapshot).order_by("occurred_at")
        )

        return UserMapper.to_domain(snapshot=snapshot, transitions=transitions_list)


    @staticmethod
    def _is_same_persisted_snapshot(
        *,
        snapshot: UserModel,
        state: str,
        activated_at: datetime | None,
        suspended_at: datetime | None,
        inactivated_at: datetime | None,
        unlocked_at: datetime | None,  
        version: int,
    ) -> bool:
        return (
            snapshot.state == state
            and snapshot.activated_at == activated_at
            and snapshot.suspended_at == suspended_at
            and snapshot.inactivated_at == inactivated_at
            and snapshot.unlocked_at == unlocked_at
            and snapshot.version == version
        )

    def save(self, user: User) -> int:
        """
        Persist an existing User aggregate using optimistic concurrency control.

        Semantics:
        - Uses user.version as the origin version.
        - Updates the snapshot only if (id, version) still matches in persistence.
        - Persists the latest transition in the same transaction.
        - Returns the newly persisted version.

        Args:
            user: user aggregate to be persisted.

        Returns:
            int: Newly persisted version number.

        Raises:
            UserPersistenceNotFoundError:
            If the user snapshot does not exist.
            ConcurrencyConflictError:
            If the snapshot exists but the persisted version differs from the aggregate origin version.
            UserTechnicalPersistenceError:
            For integrity, database-level technical failures or missing  transitions list.
        """

        origin_id = user.id
        origin_version = user.version

        state = user.state.value
        activated_at = user.activated_at
        suspended_at = user.suspended_at
        inactivated_at = user.inactivated_at
        unlocked_at = user.unlocked_at


        new_version = origin_version + 1
        now = datetime.now(UTC)


        if not user.transitions:
            raise UserTechnicalPersistenceError(
                code=ErrorCodes.MISSING_TRANSITIONS,
                message="No transitions to persist for the user.",
                details={"user_id": user.id},
            )
        try:
            # Atomic block to ensure Snapshot and Transition are persisted together
            with transaction.atomic():
                updated_rows = UserModel.objects.filter(id=origin_id, version=origin_version).update(
                    state=state,
                    activated_at=activated_at,
                    suspended_at=suspended_at,
                    inactivated_at=inactivated_at,
                    unlocked_at=unlocked_at,
                    version=new_version,
                    updated_at=now
                )

                if updated_rows == 0:
                    persisted_snapshot = UserModel.objects.filter(id=origin_id).first()
                    if persisted_snapshot is not None:
                        persisted_transition = UserMapper.to_transition(
                            state_transition=user.transitions[-1],
                            user_id=origin_id,
                        )

                        if (
                            UserTransitionModel.objects.filter(
                                transition_id=persisted_transition.transition_id
                            ).exists()
                            and self._is_same_persisted_snapshot(
                                snapshot=persisted_snapshot,
                                state=state,
                                activated_at=activated_at,
                                suspended_at=suspended_at,
                                inactivated_at=inactivated_at,
                                unlocked_at=unlocked_at,
                                version=new_version,
                                )
                            ):
                            return new_version

                        raise ConcurrencyConflictError(
                            code=ErrorCodes.CONCURRENCY_CONFLICT,
                            message="The user exists, but its persisted version \
                                does not match the aggregate origin version.",
                            details={
                                "aggregate_id": user.id,
                                "expected_version": user.version,
                                "persisted_version": persisted_snapshot.version,
                                }
                        )
                    else:
                        raise UserPersistenceNotFoundError(
                            code=ErrorCodes.USER_NOT_FOUND,
                            message="The user snapshot was not found for persistence update.",
                            details={
                                        "user_id": origin_id,
                                        "origin_version": origin_version,
                                        "attempted_new_version": new_version,
                                    }
                        )
                else:
                    UserMapper.to_transition(
                        state_transition=user.transitions[-1],
                        user_id=origin_id
                    ).save()
                    return new_version
        
        except (UserPersistenceNotFoundError, ConcurrencyConflictError):
            raise

        except DatabaseError as e:
            raise UserTechnicalPersistenceError (
                code=ErrorCodes.DATABASE_ERROR,
                message="A critical error occurred on the database server.",
                details={"error": str(e)}
            ) from e


    def create(self, user: User) ->int:
        """
            Persists a new User aggregate.
            This method is strictly for creating a new user record. It must not be used to update an existing aggregate.
            Final uniqueness is guaranteed by the persistence layer (e.g., database constraints) at the moment of insertion to prevent race conditions.
            
            Returns:
                int: The initial version of the newly persisted user.

            Raises:
                UserDuplicationError: Raised when the persistence layer confirms a duplication, either by an explicit ID or by the business key
                    (identity_type + identity_number or email).
                UserTechnicalPersistenceError: Raised when technical failures occur during communication with the persistence layer or when unexpected
                    integrity violations (such as missing foreign keys or null constraint violations) are encountered.

        """

        try:
            with transaction.atomic():
                snapshot = UserMapper.to_snapshot(user=user)
                snapshot.save()
                
                return snapshot.version

            
        except IntegrityError as e:

            cause = getattr(e, "__cause__", None)
            pg_code = getattr(cause, "pgcode", None)

            diag = getattr(cause, "diag", None)
            constraint = getattr(diag, "constraint_name", None) if diag else None


            # No fluxo atual de create(), uma unique violation do PostgreSQL (23505)
            # corresponde apenas aos cenários de duplicidade que este contrato trata
            # de forma uniforme: colisão explícita de id ou duplicidade da business key.
            # Se este model passar a ter outras unique constraints com semântica diferente,
            # esta regra deve ser endurecida para também inspecionar o constraint_name.
            
            if pg_code == "23505":
        
                if constraint == "unique_identity":
                    raise UserDuplicationError(
                        code=ErrorCodes.DUPLICATE_USER,
                        message="A user with the same identifiers already exists.",
                        details={
                            "constraint": constraint,
                        }
                    ) from e
                if constraint is not None and "email" in constraint:
                    raise UserDuplicationError(
                        code=ErrorCodes.DUPLICATE_EMAIL,
                        message="A user with the same email already exists.",
                        details={
                            "constraint": constraint,
                        }
                    ) from e

                raise UserDuplicationError(
                    code=ErrorCodes.DUPLICATE_USER,
                    message="A user with the same identifiers already exists.",
                    details={"error": str(e)},
                ) from e
                
            raise UserTechnicalPersistenceError(
                code=ErrorCodes.USER_CREATION_FAILED,
                message="Failed to create user due to an integrity error.",
                details={"error": str(e)},
            ) from e


        except DatabaseError as e:
            raise UserTechnicalPersistenceError(
                code=ErrorCodes.DATABASE_ERROR,
                message="Failed to create user due to a database error.",
                details={"error": str(e)},
            ) from e



