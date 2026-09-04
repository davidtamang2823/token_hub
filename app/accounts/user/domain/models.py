from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from pydantic import EmailStr, Field, field_validator
from accounts.user.domain.events import UserAddedToTenantEvent, UserRegisteredEvent, UserEmailChangeRequestEvent, UserEmailChangeRequestApprovedEvent, UserEmailChangeRequestRejectedEvent, UserVerifyEmailChangeEvent
from core.events import BaseEvent
from core.domain import AggregateRoot
from accounts.user.domain.enumns.email_change_request_enum import EmailChangeRequestEnum


EMAIL_CHANGE_REQUEST_TTL = timedelta(hours=48)

class UserModel(AggregateRoot):

    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool 
    is_staff: bool
    hashed_password: str | None = None
    verified_at: datetime | None = None
    verification_token: str | None = None
    verification_token_created_at: datetime | None = None
    id: UUID | None = Field(default_factory=uuid4)
    is_deleted: bool | None = False


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
        user_id: UUID,
        first_name: str,
        last_name: str, 
        hashed_password: str,
        email: str,
        is_active: bool,
        is_staff: bool,
        is_deleted: bool,
        verification_token: str, 
        verification_token_created_at: datetime,
    ) -> "User":

        return cls(
            id=user_id,
            first_name = first_name,
            last_name = last_name,
            email = email,
            is_staff = is_staff,
            is_active = is_active,
            is_deleted = is_deleted,
            verification_token=verification_token,
            verification_token_created_at=verification_token_created_at,
            hashed_password = hashed_password,
            events = [
                UserRegisteredEvent(
                    send_to = email,
                    verification_token = verification_token
                )
            ]
        )

class EmailChangeRequestModel(AggregateRoot):

    id: UUID
    old_email: EmailStr
    new_email: EmailStr
    user_id: UUID
    new_email_verification_token: str | None = None
    new_email_verification_token_created_at: datetime | None = None
    status: EmailChangeRequestEnum

    @classmethod
    def create(
        cls, 
        old_email: str, 
        new_email: str,
        user_id: UUID,
        status: "EmailChangeRequestEnum",
        send_to: list[str],
        send_by_first_name: str | None = None,
        send_by_last_name: str | None = None,
        tenant_id: UUID | None = None,
        tenant_name: str | None = None,
        tenant_code: str | None = None
    ) -> "EmailChangeRequestModel":

        return cls(
            id=uuid4(),
            old_email=old_email,
            new_email=new_email,
            new_email_verification_token=new_email_verification_token,
            new_email_verification_token_created_at=new_email_verification_token_created_at,
            status=status,
            events = [
                UserEmailChangeRequestEvent(
                    send_to=send_to,
                    send_by=old_email,
                    new_email=new_email,
                    send_by_first_name=send_by_first_name,
                    send_by_last_name=send_by_last_name,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    tenant_code=tenant_code,
                    tenant_name=tenant_name
                )
            ]
        )

    @classmethod
    def update(
        cls,
        email_change_request_id: UUID,
        status: "EmailChangeRequestEnum",
        send_to: str,
        old_email: str,
        new_email: str,
        user_id: UUID,
        send_by_first_name: str | None = None,
        send_by_last_name: str | None = None,
        new_email_verification_token: str | None = None, 
        new_email_verification_token_created_at: datetime | None = None,
        tenant_id: UUID | None = None,
        tenant_name: str | None = None,
        tenant_code: str | None = None,
    ):
        events = []

        if status == EmailChangeRequestEnum.APPROVED:
            events.append(
                UserEmailChangeRequestApprovedEvent(
                    send_to=send_to,
                    approved_by_email=old_email,
                    approved_by_first_name=send_by_first_name,
                    approved_by_last_name=send_by_last_name,
                    tenant_id=tenant_id,
                    tenant_code=tenant_code,
                    tenant_name=tenant_name
                )
            )

        elif status == EmailChangeRequestEnum.REJECTED:
            events.append(
                UserEmailChangeRequestRejectedEvent(
                    send_to=send_to,
                    rejected_by_email=old_email,
                    rejected_by_first_name=send_by_first_name,
                    rejected_by_last_name=send_by_last_name,
                    tenant_id=tenant_id,
                    tenant_code=tenant_code,
                    tenant_name=tenant_name
                )
            )

        return cls(
            id=email_change_request_id,
            old_email=old_email,
            new_email=new_email,
            new_email_verification_token=new_email_verification_token,
            new_email_verification_token_created_at=new_email_verification_token_created_at,
            user_id=user_id,
            status=status,
            events = events
        )


    @classmethod
    def verify(
        cls,
        email_change_request_id: UUID,
        status: "EmailChangeRequestEnum",
        send_to: str,
        old_email: str,
        new_email: str,
        user_id: UUID,
        new_email_verification_token: str | None = None, 
        new_email_verification_token_created_at: datetime | None = None,
    ) -> "EmailChangeRequestModel":

        events = [
            UserVerifyEmailChangeEvent(
                send_to=send_to,
            )
        ]

        return cls(
            id=email_change_request_id,
            old_email=old_email,
            new_email=new_email,
            new_email_verification_token=None,
            new_email_verification_token_created_at=None,
            user_id=user_id,
            status=status,
            events=events,
        )



    @property
    def is_expired(self) -> bool:
        return datetime.now(tz=timezone.utc) > self.new_email_verification_token_created_at + EMAIL_CHANGE_REQUEST_TTL


class UserTenantModel(AggregateRoot):

    role_id: UUID
    user_id: UUID
    email: EmailStr | None = None
    tenant_id: UUID | None = None
    created_by_id: UUID | None = None


    @classmethod
    def create(cls, email: str, role_id: UUID, tenant_id: UUID, user_id:UUID, tenant_name: str, tenant_code: str, created_by_id: UUID) -> "UserTenantModel":

        return cls(
            email = email,
            tenant_id = tenant_id,
            role_id = role_id,
            created_by_id = created_by_id,
            user_id = user_id,
            events = [
                UserAddedToTenantEvent(
                    send_to = email,
                    tenant_name = tenant_name,
                    tenant_code = tenant_code
                )
            ]
        )

    @classmethod
    def create_for_staff(cls, role_id: UUID, user_id: UUID, created_by_id: UUID) -> "UserTenantModel":

        return cls(
            role_id = role_id,
            user_id = user_id,
            created_by_id = created_by_id
        )

