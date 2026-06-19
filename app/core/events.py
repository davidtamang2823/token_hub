import typing
from datetime import datetime, timezone
from uuid import UUID, uuid4
from dataclasses import dataclass, field

@dataclass
class BaseEvent:

    event_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default=lambda : datetime.now(timezone.utc))
    event_type: str = field(init=False)


class EventBus:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_events'):
            self._events: typing.Dict[str, typing.List[typing.Callable]] = {}

    def subscribe(self, event_type: str):

        def add_event(func: typing.Callable):
            if self._events.get(event_type) is None:
                self._events[event_type] = []
            self._events.get(event_type).append(func)
            return func

        return add_event

    def publish(self, events: typing.List):
        for event in events:
            event_callables = self._events.get(event.event_type, [])
            for event_callable in event_callables:
                event_callable()


class EventTypes:
    
    # auth events
    AUTH_EMAIL_VERIFIED = "auth.email_verified"
    AUTH_PASSWORD_RESET_REQUESTED = "auth.password_reset_requested"
    AUTH_PASSWORD_RESET = "auth.password_reset"
    AUTH_LOGIN = "auth.login"

    # user events
    USER_REGISTERED = "user.registered"
    USER_BLOCKED = "user.blocked"
    USER_UNBLOCKED = "user.unblocked"

    # tenant events
    TENANT_CREATED = "tenant.created"
    TENANT_USER_ADDED = "tenant.user_added"
    TENANT_USER_REMOVED = "tenant.user_removed"
    TENANT_USER_ROLE_CHANGED = "tenant.user_role_changed"


event_bus=EventBus()
