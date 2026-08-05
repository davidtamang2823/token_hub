from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import EmailStr, Field, field_validator
from accounts.user.domain.events import UserAddedToTenant, UserRegistered
from core.events import BaseEvent
from core.domain import AggregateRoot


class UserModel(AggregateRoot):

    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool 
    is_staff: bool
    verification_token: str | None = None
    verification_token_created_at: datetime | None = None
    id: UUID | None = Field(default_factory=uuid4)


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
        return cls.validate_name(value).capitalize()

    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, value: str) -> str:
        return cls.validate_name(value).capitalize()

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str, 
        email: str,
        is_active: bool,
        is_staff: bool, 
        verification_token: str, 
        verification_token_created_at: datetime
    ) -> "User":
        user_id = uuid4()

        return cls(
            id=user_id,
            first_name = first_name,
            last_name = last_name,
            email = email,
            is_staff = is_staff,
            verification_token=verification_token,
            verification_token_created_at=verification_token_created_at,
            events = [
                UserRegistered(
                    send_to = email,
                    verification_token = verification_token
                )
            ]
        )

class UserTenantModel(AggregateRoot):

    email: EmailStr
    tenant_id: UUID
    role_id: UUID
    created_by_id: UUID | None = None


    @classmethod
    def create(cls, email: str, role_id: UUID, tenant_id: UUID, tenant_name: str, tenant_code: str, created_by_id: UUID) -> "UserTenant":

        return cls(
            email = email,
            tenant_id = tenant_id,
            role_id = role_id,
            created_by_id = created_by_id,
            events = [
                UserAddedToTenant(
                    send_to = email,
                    tenant_name = tenant_name,
                    tenant_code = tenant_code
                )
            ]
        )


