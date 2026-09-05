from accounts.user.domain.events import (
    UserRegisteredEvent, 
    UserAddedToTenantEvent, 
    UserEmailChangeRequestApprovedEvent, 
    UserEmailChangeRequestEvent, 
    UserEmailChangeRequestRejectedEvent, 
    UserVerifyEmailChangeEvent,
    UserEmailChangeVerifyEvent
)
from accounts.user.infrastructure.tasks import (
    send_welcome_verify_email_task, 
    send_user_added_to_tenant_task,
    send_user_email_change_request_approved_task,
    send_user_email_change_request_rejected_task,
    send_user_email_changed_task,
    send_user_email_change_request_task,
    send_user_email_change_verify_task
)
from core.events import event_bus, EventTypes

@event_bus.subscribe(event_type=EventTypes.USER_REGISTERED)
def send_welcome_verify_email_handler(event: UserRegisteredEvent):
    payload = event.to_dict()
    send_welcome_verify_email_task.apply_async(args=[payload])

@event_bus.subscribe(event_type=EventTypes.USER_ADDED_TO_TENANT)
def send_user_added_to_tenant_email_handler(event: UserAddedToTenantEvent):
    payload = event.to_dict()
    send_user_added_to_tenant_task.apply_async(args=[payload])

@event_bus.subscribe(event_type=EventTypes.USER_EMAIL_CHANGE_REQUEST)
def send_user_email_change_request_handler(event: UserEmailChangeRequestEvent):
    payload = event.to_dict()
    send_user_email_change_request_task.apply_async(args=[payload])

@event_bus.subscribe(event_type=EventTypes.USER_EMAIL_CHANGE_REQUEST_APPROVED)
def send_user_email_change_request_approved_handler(event: UserEmailChangeRequestApprovedEvent):
    payload = event.to_dict()
    send_user_email_change_request_approved_task.apply_async(args=[payload])

@event_bus.subscribe(event_type=EventTypes.USER_EMAIL_CHANGE_REQUEST_REJECTED)
def send_user_email_change_request_rejected_handler(event: UserEmailChangeRequestRejectedEvent):
    payload = event.to_dict()
    send_user_email_change_request_rejected_task.apply_async(args=[payload])

@event_bus.subscribe(event_type=EventTypes.USER_EMAIL_CHANGED)
def send_user_email_changed_handler(event: UserEmailChangeRequestEvent):
    payload = event.to_dict()
    send_user_email_changed_task.apply_async(args=[payload])

@event_bus.subscribe(event_type=EventTypes.USER_EMAIL_CHANGE_VERIFY)
def send_user_email_change_verify_handler(event: UserEmailChangeVerifyEvent):
    payload = event.to_dict()
    send_user_email_change_verify_task.apply_async(args=[payload])