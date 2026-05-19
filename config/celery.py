# config/celery.py
import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('FarrukhApp')

# Read configuration from Django settings using the CELERY_ namespace prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover background tasks inside your installed apps (tasks.py)
app.autodiscover_tasks()