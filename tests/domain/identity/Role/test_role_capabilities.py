from datetime import UTC, datetime

import pytest

from domain.identity.role.entities.role import Role
from domain.identity.role.value_objects.capability import Capability
from domain.shared.domain_error import DomainError


def test_has_capability_success():
    role = Role.create(
        name="estudante",
        code="estudante",
        level=4,
        created_by="actor-1",
        occurred_at=datetime.now(UTC)
    )

    assert role.capabilities == frozenset({
        Capability.GRADEBOOK_STUDENT_READ,
        Capability.DASHBOARD_STUDENT_READ
    })

    assert role.has_capability(Capability.GRADEBOOK_STUDENT_READ)
    assert role.has_capability(Capability.DASHBOARD_STUDENT_READ)


def test_unknown_code_returns_empty_capabilities():
    role = Role.create(
        name="unknown_role",
        code="unknown_code",
        level=4,
        created_by="actor-1",
        occurred_at=datetime.now(UTC)
    )
    assert role.capabilities == frozenset()
   