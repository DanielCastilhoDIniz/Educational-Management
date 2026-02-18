from infrastructure.django.apps.academic.models.enrollment_model import EnrollmentModel
from infrastructure.django.apps.academic.models.enrollment_transition import EnrollmentTransitionModel

from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.academic.enrollment.value_objects.state_transition import StateTransition

from datetime import timezone, datetime


class EnrollmentMapper:
    @staticmethod
    def normalize_to_utc(dt: datetime) -> datetime:

        """
            Ensure the datetime object is UTC-aware.
            A) Protection against None: Raises a ValueError if the data is missing.
            B) Normalization: If naive, assume UTC. If aware, convert to UTC.
        """

        if dt is None:
            raise ValueError("O campo 'dt' (datetime) não pode ser None. Dado inconsistente.")

        if not isinstance(dt, datetime):
            raise TypeError(f"Esperado datetime, recebido {type(dt).__name__}")

        if dt.tzinfo is None:
            # It's naive to assume that the origin was already UTC (or applies the standard rule).
            return dt.replace(tzinfo=timezone.utc)

        # is aware: converts any time zone (Ex: -03:00) to the UTC standard (+00:00)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def to_domain(
            *,
            snapshot: EnrollmentModel,
            transitions: list[EnrollmentTransitionModel]
            ) -> Enrollment:
        """
            Convert EnrollmentModel and its related EnrollmentTransitionModels into a domain Enrollment entity.
                - snapshot: a mutable snapshot of the current state of the enrollment (EnrollmentModel)
                - transitions: a list of immutable state transitions (EnrollmentTransitionModel) ordered by occurred_at
            The method maps the flat data from the database models into rich domain objects,
            ensuring that all necessary transformations (like datetime normalization and enum conversions)
            are handled appropriately.
        """
        # ---- Snapshot fields (local variables; do NOT mutate ORM) ----
        enrollment_id = str(snapshot.id)
        student_id = str(snapshot.student_id)
        class_group_id = str(snapshot.class_group_id)
        academic_period_id = str(snapshot.academic_period_id)

        state = EnrollmentState(snapshot.state)

        concluded_at =(
            EnrollmentMapper.normalize_to_utc(snapshot.concluded_at)
            if snapshot.concluded_at else None
        )
        cancelled_at = (
            EnrollmentMapper.normalize_to_utc(snapshot.cancelled_at)
            if snapshot.cancelled_at else None
        )
        suspended_at = (
            EnrollmentMapper.normalize_to_utc(snapshot.suspended_at)
            if snapshot.suspended_at else None
        )

        snapshot.created_at = EnrollmentMapper.normalize_to_utc(snapshot.created_at)

        version = snapshot.version

        # ---- Transitions: ORM -> Domain VO (do NOT mutate ORM) ----
        domain_transitions: list[StateTransition] = []

        for t in transitions:
            from_state = t.from_state
            to_state = t.to_state

            actor_id = str(t.actor_id)
            occurred_at = t.occurred_at

            actor_id = str(actor_id)

            occurred_at = EnrollmentMapper.normalize_to_utc(occurred_at)

            domain_transitions.append(
                StateTransition(
                    from_state=EnrollmentState(from_state),
                    actor_id=actor_id,
                    to_state=EnrollmentState(to_state),
                    occurred_at=occurred_at,
                    justification=t.justification,
                )
            )

        # ---- Build aggregate once ----
        return Enrollment(
                transitions=domain_transitions,
                id=enrollment_id,
                student_id=student_id,
                class_group_id=class_group_id,
                academic_period_id=academic_period_id,
                state=state,
                concluded_at=concluded_at,
                cancelled_at=cancelled_at,
                suspended_at=suspended_at,
                created_at=snapshot.created_at,
                version=snapshot.version,
            )


    @staticmethod
    def apply_to_snapshot():
        pass

