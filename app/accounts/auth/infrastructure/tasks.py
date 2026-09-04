from celery import shared_task
from notifications.infrastructure.email_sender import email_sender
from core.config import settings

@shared_task
def send_password_reset_email_task(payload: dict):

    subject = f"{settings.app_name}, Password Reset Link"
    new_password_verification_url = f"{settings.front_end_url}/reset-password?token={payload.get("new_password_verification_token")}"
    email_sender.send_template(
        to=payload.get("send_to"),
        subject=subject,
        template_name="auth/auth_reset_password.html",
        context={
            "app_name": settings.app_name,
            "new_password_verification_url": new_password_verification_url
        }
    )