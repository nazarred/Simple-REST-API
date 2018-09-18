from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simple_api.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

import configurations

configurations.setup()

app = Celery("simple_api")
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    'hello': {
        'task': 'accounts.tasks.hello',
        'schedule': crontab()
    }
}
