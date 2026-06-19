from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Tenant(BaseModel):

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    code: str
    is_active: bool | None = True
    id: UUID | None = Field(default_factory=uuid4)
    created_by_id: UUID | None = None
    updated_by_id: UUID | None = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Tenant name should not be empty")
        if len(value) > 125:
            raise ValueError("Tenant name character length should not be greater than 125")
        return value

    @field_validator('code')
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value:
            raise ValueError("Tenant code should not be empty")
        if len(value) > 20:
            raise ValueError("Tenant code character length should not be greater than 20")
        return value

    @classmethod
    def create(cls, name: str, code: str, created_by_id: UUID, is_active: bool=True) -> "Tenant":
        return cls(
            name=name,
            code=code,
            is_active=is_active,
            created_by_id=created_by_id
        )

    @classmethod
    def update(cls, tenant_id: UUID, name: str, code: str, updated_by_id: UUID, is_active: bool) -> "Tenant":
        return cls(
            id=tenant_id,
            name=name,
            code=code,
            is_active=is_active,
            updated_by_id=updated_by_id
        )