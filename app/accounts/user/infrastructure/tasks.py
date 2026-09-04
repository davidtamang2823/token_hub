from core.celery_app import celery_app
from notifications.infrastructure.email_sender import email_sender
from core.config import settings

@celery_app.task
def send_welcome_verify_email_task(payload: dict) -> None:
    
    subject = f"Welcome To {settings.app_name}, Please Verify This Email"
    user_verification_url = f"{settings.front_end_url}/verify-email?token={payload.get("verification_token")}"
    email_sender.send_template(
        to=payload.get("send_to"),
        subject=subject,
        template_name="user/user_welcome_verify.html",
        context={
            "user_verification_url": user_verification_url,
            "app_name": settings.app_name
        }
    )

@celery_app.task
def send_user_added_to_tenant_task(payload: dict) -> None:

    subject = "You've been added to tenant"
    login_url = f"{settings.front_end_url}/login"
    email_sender.send_template(
        to=payload.get("send_to"),
        subject=subject,
        template_name="user/user_added_to_tenant.html",
        context={
            "tenant_name":payload.get("tenant_name"),
            "tenant_code":payload.get("tenant_code"),
            "app_name": settings.app_name,
            "login_url": login_url
        }
    )

@celery_app.task
def send_user_email_change_request_task(payload: dict) -> None:

    recievers = payload.get("send_to", [])
    subject = f"Email Change Request For {payload.get('send_by_first_name')} {payload.get('send_by_last_name')} ({payload.get('send_by')})"
    for reciever in recievers: 
        email_sender.send_template(
            to=reciever,
            subject=subject,
            template_name="user/user_email_change_request.html",
            context=payload
        )

@celery_app.task
def send_user_email_change_request_approved_task(payload: dict) -> None:

    reciever = payload.get("send_to")
    subject = f"Your Email Change Request Has Been Approved By {payload.get("approved_by_first_name")} {payload.get("approved_by_last_name")} ({payload.get("approved_by_email")})"
    email_sender.send_template(
        to=reciever,
        subject=subject,
        template_name="user/user_email_change_request_approved.html",
        context=payload
    )

@celery_app.task
def send_user_email_change_request_rejected_task(payload: dict) -> None:

    reciever = payload.get("send_to")
    subject = f"Your Email Change Request Has Been Rejected By {payload.get("rejected_by_first_name")} {payload.get("rejected_by_last_name")} ({payload.get("rejected_by_email")})"
    email_sender.send_template(
        to=reciever,
        subject=subject,
        template_name="user/user_email_change_request_rejected.html",
        context=payload
    )

@celery_app.task
def send_user_email_changed_task(payload: dict) -> None:

    reciever = payload.get("send_to")
    subject = "Your Email Has Been Changed"
    email_sender.send_template(
        to=reciever,
        subject=subject,
        template_name="user/user_email_changed.html",
        context=payload
    )