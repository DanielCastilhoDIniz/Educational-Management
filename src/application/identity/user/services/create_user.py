from datetime import date, datetime
from typing import cast

from application.identity.user.dto.errors.error_codes import ErrorCodes
from application.identity.user.dto.results import ApplicationResult
from application.identity.user.errors.persistence_errors import (
    UserDuplicationError,
    UserTechnicalPersistenceError,
)
from application.identity.user.ports.user_repository import UserRepository
from application.identity.user.services._state_change_flow import (
    build_persistence_failure_result,
)
from domain.identity.user.entities.user import User
from domain.identity.user.value_objects.legal_identity import LegalIdentity, LegalIdentityType


class CreateUser:
    """Application service to create a user.
    Responsibilities:
    - Orchestrate the process of creating a user, including:
    - Retrieving the user aggregate.
    - Emitting appropriate domain events (UserCreated).
    - Persisting the updated aggregate state.
    """
    repo: UserRepository

    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(
            self,
            *,
            identity_type: str,
            identity_number: str,
            identity_issuer:str,
            full_name: str,
            birth_date: date,
            created_by: str,
            email: str | None = None,
            guardian_id: str | None = None,
            occurred_at: datetime | None = None,
        ) -> ApplicationResult:

        """
        Execute the create user process.
        Steps:
        - Create a new user aggregate.
        - Persist the new aggregate state.
        """

        user = User.create(
            legal_identity=LegalIdentity(
                identity_type=LegalIdentityType(identity_type),
                identity_number=identity_number,
                identity_issuer=identity_issuer
        ),
        full_name=full_name,
        birth_date=birth_date,
        created_by=created_by,
        email=email,
        guardian_id=guardian_id,
        occurred_at=occurred_at
        )

        try:
            self.repo.create(user)
        except UserDuplicationError as e:
            return build_persistence_failure_result(
                user_id=user.id,
                action="create",
                current_state=user.state,
                code=ErrorCodes.DUPLICATE_USER,
                message="An user with the same identifiers already exists.",
                err=e,
            )
        except UserTechnicalPersistenceError as e:
            return build_persistence_failure_result(
                user_id=user.id,
                action="create",
                current_state=user.state,
                code=cast(ErrorCodes, e.code),
                message="Failed to create user due to a technical persistence error.",
                err=e,
            )
        
        return ApplicationResult(
            aggregate_id=user.id,
            changed=True,
            success=True,
            domain_events=tuple(user.pull_domain_events()),
            new_state=user.state,
            error=None
        )
    
