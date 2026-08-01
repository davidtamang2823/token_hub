from uuid import UUID
from datetime import datetime
from dataclasses import dataclass
from pydantic import EmailStr, field_validator
from core.domain import DomainModel

@dataclass
class User:

    id: UUID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    is_staff: bool
    role_id: UUID
    role_name: str
    verified_at: datetime

class UpdateUserName(DomainModel):

    first_name: str
    last_name: str

    @staticmethod
    def validate_name(value: str) -> str:
        if not value:
            raise ValueError("First name or last name should not be empty")
        if len(value) > 125:
            raise ValueError("First name or last name character length should not be greater than 125")
        return value

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        return cls.validate_name(value)

    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        return cls.validate_name(value)


    @classmethod
    def create(cls, first_name: str, last_name: str) -> "UpdateProfile":
        return cls(id=id, first_name=first_name, last_name=last_name)

class UpdateUserEmail(DomainModel):

    user_id: UUID
    email: EmailStr

class UpdateUserStatus(DomainModel):

    user_id: UUID
    is_active: bool