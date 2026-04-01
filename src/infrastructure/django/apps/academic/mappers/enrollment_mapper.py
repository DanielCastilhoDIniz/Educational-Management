import uuid

from apps.academic.enrollments.transition_id import make_transition_id
from apps.academic.models.enrollment_model import EnrollmentModel
from apps.academic.models.enrollment_transition import EnrollmentTransitionModel
from domain.academic.enrollment.entities.enrollment import Enrollment
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState
from domain.academic.enrollment.value_objects.state_transition import StateTransition


class EnrollmentMapper:
    """
        Mapper to convert between ORM models
        (EnrollmentModel and EnrollmentTransitionModel) and domain entities (Enrollment).
    """

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
        # ---- Snapshot fields (local variables; do NOT mutate ORM)  (ORM -> Domain)----
        enrollment_id = str(snapshot.id)
        institution_id = str(snapshot.institution_id)
        student_id = str(snapshot.student_id)
        class_group_id = str(snapshot.class_group_id)
        academic_period_id = str(snapshot.academic_period_id)

        state: EnrollmentState = EnrollmentState(snapshot.state)

        created_at = snapshot.created_at
        concluded_at = snapshot.concluded_at
        cancelled_at = snapshot.cancelled_at
        suspended_at = snapshot.suspended_at
        reactivated_at = snapshot.reactivated_at


        version = snapshot.version

        # ---- Transitions: ORM -> Domain VO (do NOT mutate ORM) ----
        domain_transitions: list[StateTransition] = []

        for t in transitions:
            from_state: EnrollmentState = EnrollmentState(t.from_state)
            to_state: EnrollmentState = EnrollmentState(t.to_state)

            domain_transitions.append(
                StateTransition(
                    from_state=EnrollmentState(from_state),
                    actor_id=str(t.actor_id),
                    to_state=EnrollmentState(to_state),
                    occurred_at=t.occurred_at,
                    justification=t.justification,
                )
            )

        # Build aggregate once - domain validates invariants + normalizes datetimes
        return Enrollment(
                id=enrollment_id,
                institution_id=institution_id,
                student_id=student_id,
                class_group_id=class_group_id,
                academic_period_id=academic_period_id,
                state=state,
                created_at=created_at,
                concluded_at=concluded_at,
                cancelled_at=cancelled_at,
                suspended_at=suspended_at,
                reactivated_at=reactivated_at,
                version=version,
                transitions=domain_transitions,
            )

    @staticmethod
    def apply_to_snapshot(
        *,
        enrollment: Enrollment,
        snapshot: EnrollmentModel
    ) -> EnrollmentModel:
        """
            Apply the state of a domain Enrollment entity back to an EnrollmentModel snapshot.
            This is used when saving changes to the database,
            ensuring that the ORM model reflects the current state of the domain entity.
            The method updates all relevant fields in the snapshot based on the domain entity's attributes.
        """
        snapshot.id = enrollment.id
        snapshot.institution_id = enrollment.institution_id
        snapshot.student_id = enrollment.student_id
        snapshot.class_group_id = enrollment.class_group_id
        snapshot.academic_period_id = enrollment.academic_period_id
        snapshot.state = enrollment.state.value

        snapshot.concluded_at = enrollment.concluded_at
        snapshot.cancelled_at = enrollment.cancelled_at
        snapshot.suspended_at = enrollment.suspended_at
       

        snapshot.version = enrollment.version


        return snapshot

    @staticmethod
    def to_transition(
            *,
            state_transition: StateTransition,
            enrollment_id: str,

    ) -> EnrollmentTransitionModel:

        action_map = {
            EnrollmentState.CONCLUDED: EnrollmentTransitionModel.ActionChoices.CONCLUDE,
            EnrollmentState.CANCELLED: EnrollmentTransitionModel.ActionChoices.CANCEL,
            EnrollmentState.SUSPENDED: EnrollmentTransitionModel.ActionChoices.SUSPEND,
            EnrollmentState.ACTIVE: EnrollmentTransitionModel.ActionChoices.REACTIVATE,
        }

        transition_id = make_transition_id(
            enrollment_id=uuid.UUID(enrollment_id),
            occurred_at=state_transition.occurred_at,
            action=action_map[state_transition.to_state].value,
            from_state=state_transition.from_state.value,
            to_state=state_transition.to_state.value,
            justification=state_transition.justification,
            actor_id=state_transition.actor_id,
        )

        return EnrollmentTransitionModel(
            enrollment_id=enrollment_id,
            transition_id=transition_id,
            occurred_at=state_transition.occurred_at,
            action=action_map[state_transition.to_state],
            from_state=state_transition.from_state.value,
            to_state=state_transition.to_state.value,
            justification=state_transition.justification,
            actor_id=state_transition.actor_id,
        )
