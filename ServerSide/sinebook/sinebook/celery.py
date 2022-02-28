from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

class CeleryConfig:
    broker_url = 'redis://127.0.0.1:6379'
    accept_content = ['application/json']
    result_serializer = 'json'
    task_serializer = 'json'
    result_backend = 'django-db'
    beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinebook.settings')

app = Celery('sinebook')
app.config_from_object(CeleryConfig)

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'reqeust.........{self.request}')