import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalog_project.settings')
app = Celery('catalog_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
