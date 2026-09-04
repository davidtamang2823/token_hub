from dataclasses import dataclass
from core.events import BaseEvent, EventTypes


@dataclass
class UserResendVerificationEvent(BaseEvent):

    send_to: str
    verification_token: str

    def __post_init__(self):
        self.event_type = EventTypes.USER_RESEND_VERIFICATION

@dataclass
class PasswordResetVerificationEvent(BaseEvent):

    send_to: str
    new_password_verification_token: str

    def __post_init__(self):
        self.event_type = EventTypes.USER_PASSWORD_RESET_REQUEST