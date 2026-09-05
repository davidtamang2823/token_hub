from dataclasses import dataclass
from core.events import BaseEvent, EventTypes


@dataclass
class UserRegisteredEvent(BaseEvent):

    send_to: str
    verification_token: str

    def __post_init__(self):

        self.event_type = EventTypes.USER_REGISTERED


@dataclass
class UserAddedToTenantEvent(BaseEvent):

    send_to: str
    tenant_name: str
    tenant_code: str

    def __post_init__(self):

        self.event_type = EventTypes.USER_ADDED_TO_TENANT

@dataclass
class UserEmailChangeRequestEvent(BaseEvent):

    send_to: list[str]
    send_by: str
    new_email: str
    send_by_first_name: str
    send_by_last_name: str
    tenant_name: str | None = None
    tenant_code: str | None = None
    tenant_id: str | None = None

    def __post_init__(self):

        self.event_type = EventTypes.USER_EMAIL_CHANGE_REQUEST


@dataclass
class UserEmailChangeRequestApprovedEvent(BaseEvent):

    send_to: str
    approved_by_email: str
    approved_by_first_name: str
    approved_by_last_name: str
    tenant_name: str | None = None
    tenant_code: str | None = None
    tenant_id: str | None = None

    def __post_init__(self):

        self.event_type = EventTypes.USER_EMAIL_CHANGE_REQUEST_APPROVED


@dataclass
class UserEmailChangeRequestRejectedEvent(BaseEvent):

    send_to: str
    rejected_by_email: str
    rejected_by_first_name: str
    rejected_by_last_name: str
    tenant_name: str | None = None
    tenant_code: str | None = None
    tenant_id: str | None = None

    def __post_init__(self):

        self.event_type = EventTypes.USER_EMAIL_CHANGE_REQUEST_REJECTED

@dataclass
class UserEmailChangeVerifyEvent(BaseEvent):

    send_to: str
    new_email_verification_token: str

    def __post_init__(self):

        self.event_type = EventTypes.USER_EMAIL_CHANGE_VERIFY


@dataclass
class UserVerifyEmailChangeEvent(BaseEvent):

    send_to: str
    tenant_name: str | None = None
    tenant_code: str | None = None
    tenant_id: str | None = None

    def __post_init__(self):

        self.event_type = EventTypes.USER_EMAIL_CHANGED