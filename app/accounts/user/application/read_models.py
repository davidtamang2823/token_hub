from uuid import UUID
from datetime import datetime
from core.domain import DomainModel


class UserReadModel(DomainModel):

    id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool
    is_staff: bool
    is_deleted: bool
    role_id: UUID | None = None
    role_name: str | None = None
    verified_at: datetime | None = None