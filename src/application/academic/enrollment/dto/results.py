from __future__ import annotations
from dataclasses import dataclass

from application.academic.enrollment.dto.errors.application_error import ApplicationError

from domain.academic.enrollment.events.enrollment_events import DomainEvent
from domain.academic.enrollment.value_objects.enrollment_status import EnrollmentState


@dataclass(frozen=True, kw_only=True)
class ApplicationResult:
    """
    Base class for application results.
    """
    aggregate_id: str
    success: bool
    changed: bool
    domain_events: tuple[DomainEvent, ...] = ()
    new_state: EnrollmentState | None = None
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