from core.events import EventBus, EventTypes
from accounts.auth.domain.events import UserResendVerificationEvent, PasswordResetVerificationEvent
from accounts.user.infrastructure.tasks import send_welcome_verify_email_task

@EventBus.subscribe(EventTypes.USER_RESEND_VERIFICATION)
def resend_verification_handler(event: UserResendVerificationEvent):
    payload = event.to_dict()
    send_welcome_verify_email_task.apply_async(args=[payload])

@EventBus.subscribe(EventTypes.USER_PASSWORD_RESET_REQUEST)
def password_reset_request_handler(event: PasswordResetVerificationEvent):
    payload = event.to_dict()
    