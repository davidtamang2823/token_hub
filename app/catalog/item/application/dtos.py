from uuid import UUID
from decimal import Decimal
from core.domain import DomainModel


class CreateItemDTO(DomainModel):

    name: str
    unit_price: Decimal
    description: str | None = None
    item_group_id: UUID
    is_active: bool
    is_available: bool



class UpdateItemDTO(CreateItemDTO):

    id: UUID


class UpdateItemAvailabilityDTO(DomainModel):

    id: UUID
    is_available: bool