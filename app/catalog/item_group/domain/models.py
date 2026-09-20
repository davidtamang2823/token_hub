from uuid import UUID, uuid4
from pydantic import field_validator
from core.domain import DomainModel

class ItemGroupModel(DomainModel):

    id: UUID
    name: str
    category_id: UUID
    tenant_id: UUID
    description: str | None = None
    created_by_id: UUID | None = None
    updated_by_id: UUID | None = None


    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if not value or  len(value) > 150:
            raise ValueError("Item group name should be at least 1 and less than 150 charater length")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str):
        if not value:
            return None
        if len(value) > 500:
            raise ValueError("Category description should be less than 500 charater length")
        return value

    @classmethod
    def create(
        cls, 
        name: str, 
        description: str | None, 
        category_id: UUID, 
        tenant_id: UUID, 
        created_by_id: UUID
    ):

        return cls(
            id = uuid4(),
            name = name,
            description = description,
            category_id = category_id,
            tenant_id = tenant_id,
            created_by_id = created_by_id
        )

    @classmethod
    def update(
        cls, 
        item_group_id: UUID, 
        name: str, 
        description: str | None, 
        category_id: UUID, 
        tenant_id: UUID, 
        updated_by_id: UUID
    ):

        return cls(
            id = item_group_id,
            name = name,
            description = description,
            category_id = category_id,
            tenant_id = tenant_id,
            updated_by_id = updated_by_id
        )