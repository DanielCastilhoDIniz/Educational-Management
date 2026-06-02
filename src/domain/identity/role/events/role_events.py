from dataclasses import dataclass

from domain.identity.role.value_objects.role_status import RoleStatus
from domain.shared.domain_error import DomainError
from domain.shared.domain_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class RoleCreated(DomainEvent):
    actor_id: str
    name: str
    level: int
    code: str

    def __post_init__(self):
        required_fields_str = {
            "actor_id": ("invalid_actor_id", "Role must have a valid actor ID"),
            "name": ("invalid_name", "Role must have a valid name"), 
            "code": ("invalid_code", "Role must have a valid code")     
        }
        for field_value, (code, message) in required_fields_str.items():
            value_str = getattr(self,field_value)
            if value_str is None or not value_str.strip():
                raise DomainError(code=code, message=message)

        if self.level is None or not isinstance(self.level, int):
            raise DomainError(
                code="invalid_level",
                message="Role must be a valid level"
            )     


@dataclass(frozen=True, kw_only=True)
class RoleReactivated(DomainEvent):
    from_status: RoleStatus
    actor_id:str
    to_status: RoleStatus
  

@dataclass(frozen=True, kw_only=True)
class RoleDeactivated(DomainEvent):
    from_status: RoleStatus
    actor_id:str
    to_status: RoleStatus
