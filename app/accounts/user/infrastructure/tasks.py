from celery import shared_task
from notifications.infrastructure.email_sender import email_sender
from core.config import settings

@shared_task
def send_welcome_verify_email_task(payload: dict) -> None:
    
    subject = f"Welcome To {settings.app_name}, Please Verify This Email"
    user_verification_url = f"{settings.front_end_url}/verify-email?token={payload.get("verification_token")}"
    email_sender.send_template(
        to=payload.get("send_to"),
        subject=subject,
        template_name="user_welcome_verify.html",
        context={
            "user_verification_url": user_verification_url,
            "app_name": settings.app_name
        }
    )

@shared_task
def send_user_added_to_tenant_task(payload: dict) -> None:

    subject = "You've been added to tenant"
    login_url = f"{settings.front_end_url}/login"
    email_sender.send_template(
        to=payload.get("send_to"),
        subject=subject,
        template_name="user_added_to_tenant.html",
        context={
            "tenant_name":payload.get("tenant_name"),
            "tenant_code":payload.get("tenant_code"),
            "app_name": settings.app_name,
            "login_url": login_url
        }
    )