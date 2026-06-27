from core.events import BaseEvent, EventTypes


class UserRegistered(BaseEvent):

    email: str
    verification_token: str

    def __post_init__(self):

        self.event_type = EventTypes.USER_REGISTERED


class UserAddedToTenant(BaseEvent):

    email: str
    tenant_name: str
    tenant_code: str

    def __post_init__(self):

        self.event_type = EventTypes.USER_ADDED_TO_TENANT