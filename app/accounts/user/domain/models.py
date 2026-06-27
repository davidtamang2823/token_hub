from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from accounts.user.domain.events import UserAddedToTenant, UserRegistered
from core.events import BaseEvent
from core.domain import AggregateRoot


class User(AggregateRoot):

    email: EmailStr
    id: UUID | None = Field(default_factory=uuid4)
    is_staff: bool | None = False
    is_active: bool | None = False
    first_name: str | None = None
    last_name: str | None = None
    verification_token: str | None = None
    verification_token_created_at: datetime | None = None

    @classmethod
    def create(cls, email: str, is_staff: bool, verification_token: str, verification_token_created_at: datetime) -> "User":
        user_id = uuid4()

        return cls(
            id=user_id,
            email = email,
            is_staff = is_staff,
            verification_token=verification_token,
            verification_token_created_at=verification_token_created_at,
            events = [
                UserRegistered(
                    email = email,
                    verification_token = verification_token
                )
            ]
        )

class UserTenant(AggregateRoot):

    email: EmailStr
    tenant_id: UUID


    @classmethod
    def create(cls, email: str, tenant_id: UUID, tenant_name: str, tenant_code: str) -> "UserTenant":

        return cls(
            email = email,
            tenant_id = tenant_id,
            events = [
                UserAddedToTenant(
                    email = email,
                    tenant_name = tenant_name,
                    tenant_code = tenant_code
                )
            ]
        )


