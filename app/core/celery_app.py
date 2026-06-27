from celery import Celery


celery_app = Celery('token_hub')
celery_app.config_from_object('core.celeryconfig')
celery_app.autodiscover_tasks(
    [
        "accounts.user.infrastructure"
    ]
)