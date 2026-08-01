from dataclasses import dataclass
from core.events import BaseEvent, EventTypes


@dataclass
class UserRegistered(BaseEvent):

    send_to: str
    verification_token: str

    def __post_init__(self):

        self.event_type = EventTypes.USER_REGISTERED


@dataclass
class UserAddedToTenant(BaseEvent):

    send_to: str
    tenant_name: str
    tenant_code: str

    def __post_init__(self):

        self.event_type = EventTypes.USER_ADDED_TO_TENANT