from uuid import UUID
from datetime import datetime
from core.domain import DomainModel


class UserSchema(DomainModel):

    id: UUID
    first_name: str
    last_name: str
    email: str
    is_active: bool
    is_staff: bool
    verified_at: datetime
    role_id: UUID
    role_name: str