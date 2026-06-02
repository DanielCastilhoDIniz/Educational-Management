from datetime import UTC, datetime

import pytest

from domain.identity.role.entities.role import Role
from domain.identity.role.value_objects.role_status import RoleStatus


@pytest.fixture
def make_role():
    def _make(*, status):

        now = datetime.now(UTC)

        created_at = now 
        reactivated_at = None
        deactivated_at = now if status == RoleStatus.INACTIVE else None
    

        return Role(
            id="role1_id",
            name="secretaria",
            code="secretaria",
            level=2,
            created_by="actor-1",
            created_at=created_at,
            reactivated_at=reactivated_at,
            deactivated_at=deactivated_at,
            status=status,
        )
    return _make
