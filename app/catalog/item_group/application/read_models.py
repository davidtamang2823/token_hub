from uuid import UUID
from core.domain import DomainModel

class ItemGroupReadModel(DomainModel):

    id: UUID
    name: str
    category_id: UUID
    category_name: str
    description: str | None = None