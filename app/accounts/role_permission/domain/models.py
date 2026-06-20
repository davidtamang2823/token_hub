from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Role(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        str_strip_whitespace=True,
    )

    name: str
    id: UUID = Field(default_factory=uuid4)
    permission_ids: list[UUID] | None = []
    tenant_id: UUID | None = None
    is_system_role: bool = False
    created_by_id: UUID | None = None
    updated_by_id: UUID | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Role name is empty")
        if len(value) > 75:
            raise ValueError("Role name must not exceed 75 characters")
        return value

    @field_validator("permission_ids")
    @classmethod
    def validate_permission_ids(cls, value: list[UUID]) -> list[UUID]:
        if value and len(set(value)) != len(value):
            raise ValueError("Duplicate permission_ids are not allowed")
        return value

    @model_validator(mode="after")
    def validate_tenant_scope(self) -> "Role":
        if self.is_system_role and self.tenant_id is not None:
            raise ValueError("System roles cannot be tied to a specific tenant")
        return self

    @classmethod
    def create(cls, name: str, permission_ids: list[UUID], created_by_id: UUID, tenant_id: UUID | None = None) -> "Role":
        return cls(
            tenant_id=tenant_id,
            name=name,
            permission_ids=permission_ids,
            is_system_role=False,
        )

    @classmethod
    def update(cls, role_id: UUID, name: str, permission_ids: list[UUID], updated_by_by_id: UUID, tenant_id: UUID | None = None) -> "Role":
        return cls(
            id=role_id,
            tenant_id=tenant_id,
            name=name,
            permission_ids=permission_ids,
            is_system_role=False,
        )

class Permission(BaseModel):

    id: UUID
    codename: str
    name: str
    description: str

