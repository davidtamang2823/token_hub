from uuid import UUID
from pydantic import BaseModel, ConfigDict


class BasePydanticModel(BaseModel):

    model_config = ConfigDict(
        from_attributes = True
    )

class RoleSchema(BasePydanticModel):

    id: UUID
    name: str
    is_system_role: bool

class RoleOptionSchema(BasePydanticModel):

    id: UUID
    name: str


class PermissionSchema(BasePydanticModel):

    id: UUID
    codename: str
    name: str
    description: str


class RolePermissionSchema(RoleSchema):

    permissions: list[PermissionSchema]


class ListPermissionSchema(BasePydanticModel):

    permissions: list[PermissionSchema]


class ListRoleOptionSchema(BasePydanticModel):

    roles: list[RoleOptionSchema]