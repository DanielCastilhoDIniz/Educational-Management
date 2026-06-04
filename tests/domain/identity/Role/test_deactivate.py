import pytest

from domain.identity.role.errors.role_errors import InvalidStateTransitionError
from domain.identity.role.value_objects.role_status import RoleStatus


def test_deactivate_role_success(make_role):
    role = make_role(status=RoleStatus.ACTIVE)

    role.deactivate(actor_id="actor-2")

    assert role.status == RoleStatus.INACTIVE
    assert role.reactivated_at is None
    assert role.deactivated_at is not None
    assert role.created_at is not None

    assert len(role._domain_events) == 1
    assert role._domain_events[-1].actor_id == "actor-2"
    assert role._domain_events[-1].from_status == RoleStatus.ACTIVE
    assert role._domain_events[-1].to_status == RoleStatus.INACTIVE
    assert role._domain_events[-1].occurred_at is not None


def test_deactivate_from_inactive_role_fails(make_role):
    role = make_role(status=RoleStatus.INACTIVE)

    with pytest.raises(InvalidStateTransitionError) as exc_info:
        role.deactivate(actor_id="actor-2")
        
    err = exc_info.value
    assert err.code == "invalid_state_transition"
    assert err.message == "Cannot transition from inactive to inactive."
    assert err.details == {
        "from": "inactive",
        "to": "inactive",
        "allowed": ["active"],
    }



