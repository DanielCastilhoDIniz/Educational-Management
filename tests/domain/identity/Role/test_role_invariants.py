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


def test_create_role_raise_error_without_level():
    with pytest.raises(DomainError) as exc_info:
        Role.create(
            name="secretaria",
            code="secretaria",
            level=None,
            created_by="actor-1",
            occurred_at=datetime.now(UTC)
        )
    err = exc_info.value
    assert err.code == "invalid_level"
    assert err.message == "level is invalid"

@pytest.mark.parametrize("level", [-1, 5])
def test_create_role_raise_error_with_invalid_level(level):
    with pytest.raises(DomainError) as exc_info:
        Role.create(
            name="secretaria",
            code="secretaria",
            level=level,
            created_by="actor-1",
            occurred_at=datetime.now(UTC)
        )
    err = exc_info.value
    assert err.code == "invalid_level"
    assert err.message == "level must be a value between 0 and 4"
    assert err.details == {"level": level}
