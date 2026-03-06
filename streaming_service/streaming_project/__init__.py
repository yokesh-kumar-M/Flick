import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'streaming_project.settings')
app = Celery('streaming_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
