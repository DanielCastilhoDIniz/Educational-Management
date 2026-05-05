from datetime import datetime

from application.identity.user.dto.results import ApplicationResult
from application.identity.user.ports.user_repository import UserRepository
from application.identity.user.services._state_change_flow import (
    build_domain_failure_result,
    build_not_found_result,
    finalize_state_change,
)
from domain.identity.user.entities.user import User
from domain.shared.domain_error import DomainError


class ActivateUserService:
    """Application service to activate a user.
        Responsibilities:
    - Orchestrate the process of activating a user, including:
    - Retrieving the user aggregate
    - Emitting appropriate domain events (UserActivate).
    - Persisting the updated aggregate state.
    """
    repo: UserRepository

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(
            self,
            *,
            user_id: str,
            actor_id: str,
            occurred_at: datetime,
        ) -> ApplicationResult:

        user = self.repo.get_by_id(user_id)
        if user is None:
            return build_not_found_result(user_id=user_id, action="activate")
        previous_state = user.state
        
        try:
            user.activate(
                actor_id=actor_id,
                occurred_at=occurred_at,
            )
        except DomainError as err:
            return build_domain_failure_result(
                user_id=user_id,
                current_state=user.state,
                action="activate",
                err=err,
            )
        return finalize_state_change(
            repo=self.repo,
            user=user,
            user_id=user_id,
            action="activate",
            previous_state=previous_state,
            persistence_failure_message="Failed to persist user activation.",
            event_without_state_change_message="Activation produced pending domain events without a state change.",
            state_changed_without_event_message="Activation changed state without emitting a domain event.",
        )
        
