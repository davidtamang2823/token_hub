from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr

class UserVerification(BaseModel):    

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    first_name: str
    last_name: str
    verification_token: str
    password: str
    hashed_password: str | None = None

class UserAuth(BaseModel):

    id: UUID
    hashed_password: str
    is_staff: bool
    is_active: bool
    verified_at: datetime | None = None