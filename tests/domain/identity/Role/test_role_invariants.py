from datetime import UTC, datetime

import pytest

from domain.identity.role.entities.role import Role
from domain.shared.domain_error import DomainError


@pytest.mark.parametrize("code", [None, "", "   "])
def test_create_role_raise_error_without_code(code):
    with pytest.raises(DomainError) as exc_info:
        Role.create(
            name="secretaria",
            code=code,
            level=2,
            created_by="actor-1",
            occurred_at=datetime.now(UTC)
        )
    err = exc_info.value
    assert err.code == "invalid_code"
    assert err.message == "code is invalid"

@pytest.mark.parametrize("name", [None, "", "   "])
def test_create_role_raise_error_without_name(name):
    with pytest.raises(DomainError) as exc_info:
        Role.create(
            name=name,
            code="secretaria",
            level=2,
            created_by="actor-1",
            occurred_at=datetime.now(UTC)
        )
    err = exc_info.value
    assert err.code == "invalid_name"
    assert err.message == "name is invalid"