from datetime import datetime
from uuid import UUID
from pydantic import EmailStr
from core.domain import DomainModel

class UserVerification(DomainModel):

    first_name: str
    last_name: str
    verification_token: str
    password: str
    hashed_password: str | None = None

class UserAuth(DomainModel):

    id: UUID
    hashed_password: str
    is_staff: bool
    is_active: bool
    verified_at: datetime | None = None