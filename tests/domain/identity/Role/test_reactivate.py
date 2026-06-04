import pytest

from domain.identity.role.errors.role_errors import InvalidStateTransitionError
from domain.identity.role.events.role_events import RoleReactivated
from domain.identity.role.value_objects.role_status import RoleStatus


def test_reactivate_role_success(make_role):
    role = make_role(status=RoleStatus.INACTIVE)

    role.reactivate(actor_id="actor-2")

    assert role.status == RoleStatus.ACTIVE
    assert role.reactivated_at is not None
    assert role.deactivated_at is not None
    assert role.created_at is not None

    assert  isinstance(role._domain_events[-1], RoleReactivated)
    assert len(role._domain_events) == 1
    assert role._domain_events[-1].actor_id == "actor-2"
    assert role._domain_events[-1].from_status == RoleStatus.INACTIVE
    assert role._domain_events[-1].to_status == RoleStatus.ACTIVE
    assert role._domain_events[-1].occurred_at is not None

def test_reactivate_from_active_role_fails(make_role):
    role = make_role(status=RoleStatus.ACTIVE)

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        role.reactivate(actor_id="actor-2")
    
    err = exc_info.value
    assert err.code == "invalid_state_transition"
    assert err.message == "Cannot transition from active to active."
    assert err.details == {
        "from": "active",
        "to": "active",
        "allowed": ["inactive"],
    }