from accounts.user.domain.events import UserRegistered, UserAddedToTenant
from accounts.user.infrastructure.tasks import send_welcome_verify_email_task, send_user_added_to_tenant_task
from core.events import event_bus, EventTypes

@event_bus.subscribe(event_type=EventTypes.USER_REGISTERED)
def send_welcome_verify_email_handler(event: UserRegistered):
    payload = event.to_dict()
    send_welcome_verify_email_task.apply_async(args=[payload])

@event_bus.subscribe(event_type=EventTypes.USER_ADDED_TO_TENANT)
def send_user_added_to_tenant_email_handler(event: UserAddedToTenant):
    payload = event.to_dict()
    send_user_added_to_tenant_task.apply_async(args=[payload])