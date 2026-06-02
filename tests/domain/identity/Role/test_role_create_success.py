from datetime import UTC, datetime

from domain.identity.role.entities.role import Role
from domain.identity.role.events.role_events import RoleCreated
from domain.identity.role.value_objects.role_status import RoleStatus


def test_create_role_success():
    # Arrange
    role = Role.create(
        name="secretaria",
        code="secretaria",
        level=2,
        created_by="actor-1",
        occurred_at=datetime.now(UTC)
    
    )

    # Assert
    assert isinstance(role, Role)
    assert role.status == RoleStatus.ACTIVE
    assert role.reactivated_at is None
    assert role.deactivated_at is None
    assert role.created_at is not None
    assert role.created_by == "actor-1"

    assert role.id is not None
    assert role.name == "secretaria"
    assert role.code == "secretaria"
    assert role.level == 2

    assert len(role._domain_events) == 1
    e = role._domain_events[-1]
    assert isinstance(e, RoleCreated)
    assert e.aggregate_id == role.id
    assert e.actor_id == "actor-1"
    assert e.name == "secretaria"
    assert e.level == 2
    assert e.code == "secretaria"
    assert e.occurred_at is not None
    assert e.occurred_at == role.created_at
    assert e.event_id is not None


    