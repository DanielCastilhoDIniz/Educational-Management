import uuid

from apps.identity.models.user_model import UserModel
from apps.identity.models.user_transition_model import UserTransitionModel
from apps.identity.users.transition_id import make_user_transition_id
from domain.identity.user.entities.user import User
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType
from domain.identity.user.value_objects.user_state import UserState
from domain.identity.user.value_objects.user_transition import UserTransition


class UserMapper:
    """
        Mapper to convert between ORM models
        (UserModel and UserTransitionModel) and domain entities (User).
    """
    @staticmethod
    def to_domain(
            *,
            snapshot: UserModel,
            transitions: list[UserTransitionModel]
            
    ) -> User:
        """
            Convert UserModel and its related UserTransitionModels into a domain User entity.
                - snapshot: a mutable snapshot of the current state of the user (UserModel)
                - transitions: a list of immutable state transitions (UserTransitionModel)
            The method maps the flat data from the database models into rich domain objects,
            ensuring that all necessary transformations (like datetime normalization and enum conversions)
            are handled appropriately.
        """

        user_id = str(snapshot.id)
        identity_type = snapshot.identity_type
        identity_number = snapshot.identity_number
        identity_issuer = snapshot.identity_issuer
        full_name = snapshot.full_name
        email = snapshot.email
        birth_date = snapshot.birth_date
        guardian_id = str(snapshot.guardian_id) if snapshot.guardian_id is not None else None
        created_by = str(snapshot.created_by)

        state: UserState = UserState(snapshot.state)

        created_at = snapshot.created_at
        activated_at = snapshot.activated_at
        suspended_at = snapshot.suspended_at
        inactivated_at = snapshot.inactivated_at
        unlocked_at = snapshot.unlocked_at

        version = snapshot.version

        domain_transitions: list[UserTransition] = []

        for t in transitions:
            from_state: UserState = UserState(t.from_state)
            to_state: UserState = UserState(t.to_state)

            domain_transitions.append(
                UserTransition(
                    from_state=from_state,
                    actor_id=str(t.actor_id),
                    to_state=to_state,
                    occurred_at=t.occurred_at,
                    justification=t.justification,
                )
            )

        legal_identity = LegalIdentity(
            identity_type=LegalIdentityType(identity_type),
            identity_number=identity_number,
            identity_issuer=identity_issuer,
        )

        return User(
            id=user_id,
            legal_identity=legal_identity,
            full_name=full_name,
            birth_date=birth_date,
            created_by=created_by,
            email=email,
            guardian_id=guardian_id,
            state=state,
            created_at=created_at,
            activated_at=activated_at,
            suspended_at=suspended_at,
            inactivated_at=inactivated_at,
            unlocked_at=unlocked_at,
            version=version,
            transitions=domain_transitions,
        )
    
    @staticmethod
    def to_snapshot(
        *,
        user: User,
    ) -> UserModel:
        
        return UserModel(
            id=user.id,
            identity_type=user.legal_identity.identity_type.value,
            identity_number=user.legal_identity.identity_number,
            identity_issuer=user.legal_identity.identity_issuer,
            full_name=user.full_name,
            email=user.email,
            birth_date=user.birth_date,
            guardian_id=user.guardian_id,
            state=user.state.value,
            created_by=user.created_by,
            created_at=user.created_at,
            activated_at=user.activated_at,
            suspended_at=user.suspended_at,
            inactivated_at=user.inactivated_at,
            unlocked_at=user.unlocked_at,
            version=user.version,  
        )
    
    @staticmethod
    def to_transition(
            *,
            state_transition: UserTransition,
            user_id: str,
    ) -> UserTransitionModel:
        
        action_map: dict[tuple[UserState, UserState], UserTransitionModel.ActionChoices] = {
            (UserState.PENDING,   UserState.ACTIVE):    UserTransitionModel.ActionChoices.ACTIVATE,
            (UserState.PENDING,   UserState.INACTIVE):  UserTransitionModel.ActionChoices.INACTIVATE,
            (UserState.ACTIVE,    UserState.SUSPENDED): UserTransitionModel.ActionChoices.SUSPEND,
            (UserState.ACTIVE,    UserState.INACTIVE):  UserTransitionModel.ActionChoices.INACTIVATE,
            (UserState.SUSPENDED, UserState.ACTIVE):    UserTransitionModel.ActionChoices.UNLOCK,
            (UserState.SUSPENDED, UserState.INACTIVE):  UserTransitionModel.ActionChoices.INACTIVATE,
        }

        transition_id = make_user_transition_id(
            user_id=uuid.UUID(user_id),
            action=action_map[(state_transition.from_state, state_transition.to_state)],
            from_state=state_transition.from_state.value,
            to_state=state_transition.to_state.value,
            occurred_at=state_transition.occurred_at,
            actor_id=state_transition.actor_id,
            justification=state_transition.justification,
        )

        return UserTransitionModel(
            transition_id=transition_id,
            user_id=user_id,
            occurred_at=state_transition.occurred_at,
            action=action_map[(state_transition.from_state, state_transition.to_state)],
            from_state=state_transition.from_state.value,
            to_state=state_transition.to_state.value,
            justification=state_transition.justification,
            actor_id=state_transition.actor_id,
        )



        
