import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subscription_billing.settings")

app = Celery("subscription_billing")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
