from uuid import UUID
from pydantic import BaseModel, ConfigDict


class BasePydanticModel(BaseModel):

    model_config = ConfigDict(
        from_attributes = True
    )

class Role(BasePydanticModel):

    id: UUID
    name: str
    is_system_role: bool

class RoleOption(BasePydanticModel):

    id: UUID
    name: str


class Permission(BasePydanticModel):

    id: UUID
    codename: str
    name: str
    description: str


class RolePermissionSchema(Role):

    permissions: list[Permission]


class ListPermissionSchema(BasePydanticModel):

    permissions: list[Permission]


class ListRoleOptionSchema(BasePydanticModel):

    roles: list[RoleOption]