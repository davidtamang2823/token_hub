from celery import shared_task

@shared_task
def send_welcome_verify_email(payload: dict): ...