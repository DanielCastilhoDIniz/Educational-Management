from datetime import datetime

from application.identity.user.dto.results import ApplicationResult
from application.identity.user.ports.user_repository import UserRepository
from application.identity.user.services._state_change_flow import (
    build_domain_failure_result,
    build_not_found_result,
    finalize_state_change,
)
from domain.shared.domain_error import DomainError


class UnlockUserService:
    """Application service to unlock a suspended user.
    Responsibilities:
    - Orchestrate the process of unlocking a user, including:
    - Retrieving the user aggregate.
    - Emitting appropriate domain events (UserUnlocked).
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
            justification: str,
            occurred_at: datetime | None = None,
        ) -> ApplicationResult:

        user = self.repo.get_by_id(user_id)
        if user is None:
            return build_not_found_result(user_id=user_id, action="unlock")
        
        previous_state = user.state
        
        try:
            user.unlock(
                actor_id=actor_id,
                occurred_at=occurred_at,
                justification=justification,
            )
        except DomainError as err:
            return build_domain_failure_result(
                user_id=user_id,
                current_state=user.state,
                action="unlock",
                err=err,
            )

        return finalize_state_change(
            repo=self.repo,
            user=user,
            user_id=user_id,
            action="unlock",
            previous_state=previous_state,
            persistence_failure_message="Failed to persist user unlocking.",
            event_without_state_change_message="Unlocking produced pending domain events without a state change.",
            state_changed_without_event_message="Unlocking changed state without emitting a domain event.",
        )
