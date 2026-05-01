from __future__ import annotations

from dataclasses import dataclass

from application.shared.application_error import ApplicationError
from domain.identity.user.value_objects.user_state import UserState
from domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class ApplicationResult:
    """
        Stable output contract returned by Application Services (Contract A).

        Represents one of:
        - Success with change (domain_events + new_state present),
        - Success with no-op (no events, no new_state),
        - Failure (error present; no change, no events).
    """

    aggregate_id: str | None
    success: bool
    changed: bool
    domain_events: tuple[DomainEvent, ...] = ()
    new_state: UserState | None = None
    error: ApplicationError | None = None

    def __post_init__(self) -> None:
        if not self.success:
            self._validate_failure_contract()
            return
        self._validate_success_contract()


    def _validate_failure_contract(self) -> None:
            if self.error is None:
                raise ValueError("If 'success' is False, 'error' is required.")
            if self.changed:
                raise ValueError("If 'success' is False, 'changed' must be False.")
            if self.domain_events:
                raise ValueError("If 'success' is False, 'domain_events' must be empty.")
            if self.new_state is not None:
                raise ValueError("If 'success' is False, 'new_state' must be None.")

    def _validate_success_contract(self) -> None:
        if self.error is not None:
            raise ValueError("If 'success' is True, 'error' must be None.")
        self._validate_change_contract()

    def _validate_change_contract(self) -> None:
        if self.changed:
            if not self.domain_events:
                raise ValueError("If 'changed' is True, 'domain_events' must not be empty.")
            if self.new_state is None:
                raise ValueError("If 'changed' is True, 'new_state' is required.")
            return

        if self.domain_events:
            raise ValueError("If 'changed' is False, 'domain_events' must be empty.")
        if self.new_state is not None:
            raise ValueError("If 'changed' is False, 'new_state' must be None.")
