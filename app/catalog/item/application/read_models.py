from uuid import UUID
from decimal import Decimal
from core.domain import DomainModel

class ItemReadModel(DomainModel):

    id: UUID
    name: str
    description: str | None
    unit_price: Decimal
    is_active: bool
    is_available: bool
    item_group_id: UUID
    item_group_name: str
    category_id: UUID
    category_name: str
