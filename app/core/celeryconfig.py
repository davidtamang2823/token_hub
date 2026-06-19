from core.config import settings

broker_url = settings.celery_broker_url
result_backend = settings.celery_result_backend
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = True
imports = ()