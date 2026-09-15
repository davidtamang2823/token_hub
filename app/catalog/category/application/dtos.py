from core.domain import DomainModel

class CreateCategoryDTO(DomainModel):

    name: str
    description: str | None = None


class UpdateCategoryDTO(CreateCategoryDTO):

    id: UUID