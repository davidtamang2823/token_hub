from uuid import UUID, uuid4
from decimal import Decimal
from pydantic import field_validator, Field
from core.domain import DomainModel


class ItemModel(DomainModel):

    id: UUID
    name: str
    description: str | None
    is_active: bool
    is_available: bool
    item_group_id: UUID
    tenant_id: UUID
    unit_price: Decimal = Field(max_digits=10, decimal_places=2)
    created_by_id: UUID | None = None
    updated_by_id: UUID | None = None


    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        if not value or  len(value) > 150:
            raise ValueError("Item name should be at least 1 and less than 150 charater length")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str):
        if not value:
            return None
        if len(value) > 500:
            raise ValueError("Item description should be less than 500 charater length")
        return value

    @classmethod
    def create(
        cls, 
        name: str, 
        description: str | None, 
        unit_price: Decimal, 
        is_active: bool, 
        is_available: bool, 
        item_group_id: UUID, 
        tenant_id: UUID, 
        created_by_id: UUID
    ):

        return cls(
            id = uuid4(),
            name = name,
            description = description,
            unit_price = unit_price,
            is_active = is_active,
            is_available = is_available,
            item_group_id = item_group_id,
            tenant_id = tenant_id,
            created_by_id = created_by_id
        )
    
    @classmethod
    def update(
        cls, 
        item_id: UUID, 
        name: str, 
        description: str | None, 
        unit_price: Decimal, 
        is_active: bool, 
        is_available: bool, 
        item_group_id: UUID, 
        tenant_id: UUID, 
        updated_by_id: UUID
    ):

        return cls(
            id = item_id,
            name = name,
            description = description,
            unit_price = unit_price,
            is_active = is_active,
            is_available = is_available,
            item_group_id = item_group_id,
            tenant_id = tenant_id,
            updated_by_id = updated_by_id
        )