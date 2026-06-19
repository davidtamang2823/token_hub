from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class User(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    email: EmailStr
    id: UUID | None = Field(default_factory=uuid4)
    is_staff: bool | None = False
    is_active: bool | None = False
    first_name: str | None = None
    last_name: str | None = None
