from uuid import UUID
from core.domain import DomainModel

class CreateItemGroupDTO(DomainModel):

    name: str
    category_id : UUID
    description: str | None = None

class UpdateItemGroupDTO(CreateItemGroupDTO):

    id: UUID