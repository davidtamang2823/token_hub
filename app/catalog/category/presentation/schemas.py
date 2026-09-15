from uuid import UUID
from core.domain import DomainModel


class CategorySchema(DomainModel):

    id: UUID
    name: str
    description: str | None = None